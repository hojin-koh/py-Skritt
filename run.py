from Skritt import Step

class RunSomething(Step):
    def main(self) -> int:
        t = self.shellbg(
                ('./slowrun.sh', '15'),
                ('awk', '{print;print;fflush(stdout)}'),
                ('sed', 's/15/999/'),
                )
        t2 = self.shellbg(
                ('./slowrun.sh', '15'),
                ('awk', '{print;print;fflush(stdout)}'),
                ('sed', 's/15/999/'),
                )
        t.join()
        t2.join()
        return 0

import sys
z = RunSomething(*sys.argv[1:])
z.invoke()

