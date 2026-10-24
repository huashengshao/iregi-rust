"""Owned process-group lifecycle. Importing this module launches nothing."""
from pathlib import Path
import hashlib,os,signal,subprocess,time

class Budget:
    """Reserve eight seconds for owned cleanup and terminal bookkeeping."""
    def __init__(self,seconds):
        self.started=time.monotonic();self.seconds=seconds
        self.deadline=self.started+seconds;self.work_deadline=self.deadline-8
        self.cancelled=None;self.previous={}
    def remaining(self):
        remaining=self.work_deadline-time.monotonic()
        if self.cancelled is not None:raise RuntimeError(self.cancelled)
        if remaining<=0:raise TimeoutError('aggregate work budget exhausted; cleanup reserve retained')
        return remaining
    def arm(self):
        def interrupt(number,frame):
            self.cancelled='cancelled by signal '+str(number)
            for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGALRM):signal.signal(sig,signal.SIG_IGN)
            raise RuntimeError(self.cancelled)
        for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGALRM):
            self.previous[sig]=signal.signal(sig,interrupt)
        signal.setitimer(signal.ITIMER_REAL,max(.001,self.work_deadline-time.monotonic()))
    def disarm(self):
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in self.previous.items():signal.signal(sig,handler)
    def elapsed(self):return time.monotonic()-self.started

def digest(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def group_exists(group):
    try:os.killpg(group,0);return True
    except ProcessLookupError:return False

def cleanup(owner,result,errors):
    """Check the owned group even when its original leader has already exited."""
    group=owner.pid
    try:
        alive=group_exists(group)
        result['group_existed_at_cleanup']=alive
        if alive:
            # Leader exit is not evidence that rustc/linker descendants have exited.
            try:os.killpg(group,signal.SIGTERM)
            except ProcessLookupError:pass
            until=time.monotonic()+1
            while group_exists(group)and time.monotonic()<until:
                owner.poll();time.sleep(.025)
            if group_exists(group):
                try:os.killpg(group,signal.SIGKILL)
                except ProcessLookupError:pass
        try:owner.wait(timeout=3)
        except subprocess.TimeoutExpired:errors.append('owned process leader did not exit after SIGKILL')
        until=time.monotonic()+2
        while group_exists(group)and time.monotonic()<until:time.sleep(.025)
        result['owned_group_gone']=not group_exists(group)
        if not result['owned_group_gone']:errors.append('owned descendant process group remains after cleanup')
    except Exception as error:errors.append('owned-group cleanup: '+repr(error))

def execute(command,logpath,budget,cap,errors,persist,environment=None):
    result={'command':command,'status':'preparing','timeout_seconds':min(cap,budget.remaining())}
    owner=None;started=time.monotonic();persist(result)
    try:
        with Path(logpath).open('x')as log:
            owner=subprocess.Popen(command,env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            result.update(status='running',owned_process_group=owner.pid);persist(result)
            try:owner.wait(timeout=min(cap,budget.remaining()))
            except subprocess.TimeoutExpired:result['timeout']=True
            result['returncode']=owner.poll()
    except Exception as error:
        result['error']=repr(error)
        raise
    finally:
        if owner is not None:
            cleanup(owner,result,errors)
            result['returncode']=owner.returncode
        result['elapsed_seconds']=time.monotonic()-started
        result['status']='exited'if result.get('returncode')==0 and not result.get('timeout')and'error'not in result else'failed'
        persist(result) # Terminal event precedes post-execution reads/hashes.
    return result

def freeze_binary(source,expected,destination,budget):
    """Execute a fresh owned copy whose bytes equal the reviewed artifact."""
    budget.remaining();assert digest(source)==expected,'source executable changed'
    with Path(source).open('rb')as src,Path(destination).open('xb')as dst:
        while block:=src.read(1024*1024):budget.remaining();dst.write(block)
    Path(destination).chmod(0o500)
    assert digest(destination)==expected,'frozen executable copy differs'
    return Path(destination)
