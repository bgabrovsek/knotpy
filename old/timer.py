from datetime import datetime


timers = dict()
timer_start_tm = dict()

def timer_start(name):
    global timers, timer_start_tm

    if 'global' not in timers:
        timers['global'] = 0.0
        timer_start_tm['global'] = datetime.utcnow()

    if name not in timers:
        timers[name] = 0.0
    timer_start_tm[name] = datetime.utcnow()




def timer_end(name):

    global timers, timer_start_tm

    #  print(timers, timer_start_tm)

    timers[name] += (datetime.utcnow()-timer_start_tm[name]).total_seconds()


def timer_reset_all():
    global timers, timer_start_tm
    timers = dict()
    timer_start_tm = dict()

def timer_print():
    global timers, timer_start_tm

    if 'global' not in timers:
        return

    try:

        global_timer = (datetime.utcnow()-timer_start_tm['global']).total_seconds()

        for s in timers:
            if s == 'global':
                print("Global timer:",str(global_timer)+'s')
            else:
              #  print(s,timers[s])
                print("Timer",str(s)+":", str(int(1000*timers[s]/global_timer)/10)+'%')

    except:
        print("timer errror.")



class dot_counter():
    """"
    counter for printing computational progress
    """
    def __init__(self, dot_every=1000, line_every_dots=100, print_stats = False, unit = "", quiet=False):
        """
        initialization
        :param dot_every: how many times must tick() be called to print a dot
        :param line_every_dots: number of dots per line
        :param print_stats: print stats at the end
        :param unit: kilo, mega,...
        :param quiet: should anything be printed?
        """
        self.dot_every, self.line_every_dots = dot_every, line_every_dots
        self.print_stats, self.unit, self.quiet = print_stats, unit, quiet
        self.count = 0

    def tick(self):
        self.count += 1
        if self.quiet: return

        if self.count % self.dot_every == 0:
            print(".", end="", flush=True)

        if self.count % (self.dot_every * self.line_every_dots) == 0:
            if self.print_stats:
                if self.unit == "":
                    print(" ("+str(self.count)+")", flush=True)
                if self.unit == "K" or self.unit == "k":
                    print(" (" + str(self.count/1024) + "K)", flush=True)
                if self.unit == "m" or self.unit == "M":
                    print(" (" + str((round((10*self.count)/(1024*1024)))/10) + "M)", flush=True)

            else:
                print("", flush=True)

    def end(self):
        if self.quiet: return
        if self.count < self.dot_every: return

        if self.print_stats:
            if self.unit == "":
                print(" (" + str(self.count) + ")", flush=True)
            if self.unit == "K" or self.unit == "k":
                print(" (" + str(self.count / 1024) + "K)", flush=True)
            if self.unit == "m" or self.unit == "M":
                print(" (" + str((round((10 * self.count) / (1024 * 1024))) / 10) + "M)", flush=True)

        else:
            print("", flush=True)

'''
x =  {i:i+2 for i in range(100000)}


for xxx in range(100):
    timer_start(0)
    a = 0

    for i in x:
        a += x[i]
    timer_end(0)


    timer_start(1)
    c = 0
    for i, b in x.items():
        c += b
    timer_end(1)

print(a,c)
timer_print()
'''