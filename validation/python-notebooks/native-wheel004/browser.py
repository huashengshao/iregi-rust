"""One actual browser pass over the three successful fixed-wheel exports."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import hashlib,json,os,pathlib,threading,time
ROOT=pathlib.Path.cwd();BASE=ROOT/'target/notebook-wheel004-protocol';OUT=BASE/'execution/browser';OUT.mkdir(exist_ok=True)
os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(ROOT/'.local/playwright-browsers')
from playwright.sync_api import sync_playwright
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

def main():
 requests=[];responses=[];failed=[];console=[];errors=[];views=[]
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'target/gallery')))
 threading.Thread(target=server.serve_forever,daemon=True).start();began=time.monotonic()
 paths=['wheel004-first.html','wheel004-dots.html','wheel004-benchmarks.html']
 inputs={p:hashlib.sha256((ROOT/'target/gallery'/p).read_bytes()).hexdigest() for p in paths}
 try:
  with sync_playwright() as driver:
   browser=driver.chromium.launch(headless=True,args=['--no-sandbox'],timeout=20000);version=browser.version
   for filename in paths:
    for name,width,height,color in [('desktop',1440,1100,'light'),('mobile',390,1400,'dark')]:
     label=f'{filename[:-5]}-{name}';ctx=browser.new_context(viewport={'width':width,'height':height},color_scheme=color);page=ctx.new_page()
     page.on('request',lambda r:requests.append({'url':r.url,'type':r.resource_type}))
     page.on('response',lambda r:responses.append({'url':r.url,'status':r.status}))
     page.on('requestfailed',lambda r:failed.append({'url':r.url,'failure':r.failure}))
     page.on('pageerror',lambda e:errors.append(str(e)))
     page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
     page.goto(f'http://127.0.0.1:{server.server_port}/{filename}',wait_until='domcontentloaded',timeout=20000)
     page.locator('.tirust-hero h1').wait_for(state='visible',timeout=20000);page.evaluate('document.fonts.ready')
     title=page.locator('.tirust-hero h1').inner_text();page.locator('.tirust-hero').screenshot(path=str(OUT/f'{label}-hero.png'),timeout=10000)
     record={'file':filename,'view':name,'title':title,'viewport':{'width':width,'height':height},'katex_elements':page.locator('.katex').count(),'frames':len(page.frames)}
     assert record['katex_elements']>0
     if filename=='wheel004-first.html':
      graphframe=None
      for frame in page.frames:
       if frame.locator('figcaption').filter(has_text='Feynman diagram bubble').count():graphframe=frame;break
      assert graphframe is not None,'The actual FeynKit graph iframe is absent'
      graph=graphframe.locator('figure').filter(has=graphframe.locator('figcaption').filter(has_text='Feynman diagram bubble')).first
      assert graph.locator('svg').count()>0
      graph.screenshot(path=str(OUT/f'{label}-graph.png'),timeout=10000)
      record['actual_graph_caption']=graph.locator('figcaption').inner_text();record['actual_graph_svg_count']=graph.locator('svg').count()
      cards=page.locator('.tirust-cards').last;cards.scroll_into_view_if_needed();cards.screenshot(path=str(OUT/f'{label}-laurent.png'),timeout=10000)
      record['rendered_laurent_cards']=cards.locator('.tirust-card').count();assert record['rendered_laurent_cards']==4
     elif filename=='wheel004-dots.html':
      cards=page.locator('.tirust-cards').first;cards.scroll_into_view_if_needed();cards.screenshot(path=str(OUT/f'{label}-laurent.png'),timeout=10000)
      record['rendered_laurent_cards']=cards.locator('.tirust-card').count();assert record['rendered_laurent_cards']==4
      assert 'An independent finite difference' in page.locator('body').inner_text()
     else:
      grid=page.locator('.tirust-overflow').first;grid.scroll_into_view_if_needed();grid.screenshot(path=str(OUT/f'{label}-grid-left.png'),timeout=10000)
      record['grid']=grid.evaluate('e=>({visible:e.clientWidth,content:e.scrollWidth})')
      grid.evaluate('e=>e.scrollLeft=e.scrollWidth-e.clientWidth');grid.screenshot(path=str(OUT/f'{label}-grid-right.png'),timeout=10000)
      chart=page.locator('.tirust-overflow').nth(1);chart.scroll_into_view_if_needed();chart.screenshot(path=str(OUT/f'{label}-chart-left.png'),timeout=10000)
      record['chart']=chart.evaluate('e=>({visible:e.clientWidth,content:e.scrollWidth})');assert record['chart']['content']>=930
      chart.evaluate('e=>e.scrollLeft=e.scrollWidth-e.clientWidth');chart.screenshot(path=str(OUT/f'{label}-chart-right.png'),timeout=10000)
      assert page.locator('.tirust-ratio').count()==8
      assert 'TIRust (selected) / COLLIER' in grid.inner_text() and 'inconclusive-short-block' in grid.inner_text()
      record['retained_ratio_rows']=8
     dimensions=page.evaluate('({viewport:innerWidth,document:document.documentElement.scrollWidth})');record['document']=dimensions
     assert dimensions['viewport']==dimensions['document'],dimensions
     views.append(record);ctx.close()
   browser.close()
  http_errors=[r for r in responses if r['status']>=400]
  result={'status':'PASS' if not failed and not console and not errors and not http_errors else 'FAIL','seconds':time.monotonic()-began,'browser':version,'views':views,'requests':len(requests),'failed_requests':len(failed),'console_errors':console,'page_errors':errors,'HTTP_errors':http_errors,'HTML_inputs':inputs,'HTML_unchanged':all(hashlib.sha256((ROOT/'target/gallery'/p).read_bytes()).hexdigest()==h for p,h in inputs.items()),'native_backend':False,'scope':'Real desktop/mobile static HTML display from actual fixed-wheel notebook evaluation; no reactive browser numerical backend.'}
  (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
  assert result['status']=='PASS' and result['HTML_unchanged']
 finally:
  for name,value in [('requests',requests),('responses',responses),('failed-requests',failed),('console-errors',console),('page-errors',errors),('partial-views',views)]:
   (OUT/f'{name}.json').write_text(json.dumps(value,indent=2)+'\n')
  server.shutdown();server.server_close()
if __name__=='__main__':main()
