"""Untimed line-protocol process ownership; importing launches nothing."""
import json,os,selectors,signal,subprocess,time
from lifecycle import group_exists

class Session:
    def __init__(self,label):
        self.label=label;self.owner=None;self.log=None;self.stdout_log=None;self.selector=None;self.buffer=b'';self.responses=0
    def start(self,binary,taskset,folder,budget,persist,cpu):
        budget.remaining();self.log=(folder/(self.label+'.stderr.log')).open('x');self.stdout_log=(folder/(self.label+'.stdout.log')).open('xb')
        assert type(cpu)is int and cpu>=0
        command=[taskset,'-c',str(cpu),str(binary)]
        self.owner=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,bufsize=0,start_new_session=True)
        persist({'label':self.label,'command':command,'owned_process_group':self.owner.pid,'status':'running'})
        os.set_blocking(self.owner.stdin.fileno(),False);os.set_blocking(self.owner.stdout.fileno(),False)
        self.selector=selectors.DefaultSelector();self.selector.register(self.owner.stdout,selectors.EVENT_READ)
    def drain(self):
        while True:
            try:chunk=os.read(self.owner.stdout.fileno(),65536)
            except BlockingIOError:break
            if not chunk:break
            self.stdout_log.write(chunk);self.stdout_log.flush();self.buffer+=chunk
    def no_pending_result(self):
        assert not any(line.startswith(b'RESULT ')for line in self.buffer.split(b'\n')),'unsolicited or extra RESULT line'
    def request(self,payload,budget):
        assert self.owner.poll()is None,'session already exited'
        self.drain();self.no_pending_result()
        outgoing=memoryview(payload.encode());sent=0
        self.selector.register(self.owner.stdin,selectors.EVENT_WRITE)
        try:
            while True:
                remaining=budget.remaining()
                if sent==len(outgoing):
                    while b'\n'in self.buffer:
                        line,self.buffer=self.buffer.split(b'\n',1)
                        if line.startswith(b'RESULT '):
                            self.no_pending_result();self.responses+=1;return json.loads(line[7:])
                events=self.selector.select(remaining)
                if not events:raise TimeoutError('request exhausted aggregate work budget')
                for key,_ in events:
                    if key.fileobj is self.owner.stdin:
                        try:sent+=os.write(self.owner.stdin.fileno(),outgoing[sent:])
                        except BlockingIOError:continue
                        if sent==len(outgoing):self.selector.unregister(self.owner.stdin)
                    else:
                        try:chunk=os.read(self.owner.stdout.fileno(),65536)
                        except BlockingIOError:continue
                        if not chunk:raise RuntimeError('child exited before complete RESULT')
                        self.stdout_log.write(chunk);self.stdout_log.flush();self.buffer+=chunk
        finally:
            try:self.selector.unregister(self.owner.stdin)
            except KeyError:pass

def close_all(sessions,budget,errors):
    """One shared six-second cleanup reserve for every already launched session."""
    previous={};records=[];deadline=min(time.monotonic()+6,budget.deadline-1)
    def defer(number,frame):budget.cancelled='cancelled by signal '+str(number)+' during session cleanup'
    for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGALRM):previous[sig]=signal.signal(sig,defer)
    try:
        for session in sessions:
            owner=session.owner
            if owner is not None and owner.poll()is None:
                try:os.write(owner.stdin.fileno(),b'QUIT\n')
                except Exception as error:errors.append(session.label+' quit: '+repr(error))
        graceful=min(time.monotonic()+1,deadline)
        while time.monotonic()<graceful and any(s.owner is not None and s.owner.poll()is None for s in sessions):time.sleep(.01)
        for session in sessions:
            owner=session.owner
            if owner is not None:
                try:
                    if group_exists(owner.pid):os.killpg(owner.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                except Exception as error:errors.append(session.label+' group kill: '+repr(error))
        for session in sessions:
            owner=session.owner
            try:
                if owner is not None:owner.wait(timeout=max(.001,deadline-time.monotonic()))
            except Exception as error:errors.append(session.label+' reap: '+repr(error))
        while time.monotonic()<deadline and any(s.owner is not None and group_exists(s.owner.pid)for s in sessions):time.sleep(.025)
        for session in sessions:
            owner=session.owner
            record={'label':session.label,'owned_process_group':None if owner is None else owner.pid,'returncode':None if owner is None else owner.returncode,'owned_group_gone':owner is None or not group_exists(owner.pid),'received_responses':session.responses}
            if owner is not None:
                try:session.drain();session.no_pending_result()
                except Exception as error:errors.append(session.label+' terminal stdout: '+repr(error))
            if not record['owned_group_gone']:errors.append(session.label+' owned group remains')
            records.append(record)
            for stream in ([session.selector,session.log,session.stdout_log]+([]if owner is None else[owner.stdin,owner.stdout])):
                if stream is not None:
                    try:stream.close()
                    except Exception as error:errors.append(session.label+' stream close: '+repr(error))
    finally:
        for sig,handler in previous.items():signal.signal(sig,signal.SIG_IGN if budget.cancelled else handler)
    return records
