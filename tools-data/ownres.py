import sys,io,re,os,collections,json
sys.argv=['x','dry']; exec(open('/tmp/bakedprice.py').read().split("if __name__=='__main__':")[0])
MODE=sys.argv[1] if len(sys.argv)>1 else 'dry'
import builtins
def fix(t,ns,es):
    st=collections.Counter()
    t,k=re.subn(r'Booking starts from \$%s\.'%re.escape(ns),'Prices are shown live in the booking calendar.',t); st['booking']+=k
    t,k=re.subn(r'(?<=[.!?]) From \$%s\.(?=[\s"<])'%re.escape(ns),'',t); st['from_sentence']+=k
    t,k=re.subn(r'(?<=[.!?]) Desde \$%s\.(?=[\s"<])'%re.escape(ns),'',t); st['desde_sentence']+=k
    t,k=re.subn(r' · (?:From|Desde) \$%s(?=[.\s"<])'%re.escape(ns),'',t); st['dot_from']+=k
    t,k=re.subn(r' is bookable starting from \$%s\.'%re.escape(ns),' is bookable online.',t); st['bookable']+=k
    t,k=re.subn(r'(?<=\.) (?:From|Desde) \$%s · '%re.escape(ns),' ',t); st['from_mid']+=k
    t,k=re.subn(r'(?<=[.!?]) (?:From|Desde) \$%s(?= ·|\.)'%re.escape(ns),'',t); st['from_any']+=k
    return t,st
