#این فایل مربوط به کلاس Team است
class Team:
    """
    کلاس تیم ملی فوتبال.

    مسئولیت این کلاس نگهداری اطلاعات پایه هر تیم (نام، قدرت حمله و
    دفاع، رتبه فیفا) و آمار آن در طول تورنمنت (گل زده، گل خورده،
    امتیاز) است. همچنین منطق شبیه‌سازی یک مسابقه (شامل وقت اضافه و
    پنالتی در مراحل حذفی) در این کلاس پیاده‌سازی شده است.
    """

    def __init__(self, name, attack, defense, rank):
        
        self.name = str(name)
        self.attack = int(attack)
        self.defense = int(defense)
        self.rank = int(rank)
        self.for_goals = 0
        self.against_goals = 0
        self.points = 0
        self.group = None

    def goal_difference(self):
        """محاسبه تفاضل گل تیم در طول تورنمنت."""
        return self.for_goals - self.against_goals

    def reset_stats(self):
        """صفر کردن آمار تیم (گل زده، گل خورده و امتیاز) پیش از شروع"""
        
        self.for_goals = 0
        self.against_goals = 0
        self.points = 0

    def lambda_vs(self, opponent):
        """محاسبه میانگین گل مورد انتظار (لامبدا) این تیم مقابل حریف مشخص"""
        return (self.attack / 100) * 1.5 + (1 - opponent.defense / 100) * 0.8

    def _penalty_prob_vs(self, opponent):
        """محاسبه احتمال گل شدن یک ضربه پنالتی این تیم مقابل حریف مشخص"""
        prob = 0.75 + (self.attack - opponent.defense) / 250
        return max(0.6, min(0.9, prob))

    def simulate_match(self, opponent, is_knockout=False):
        """
        شبیه‌سازی نتیجه یک مسابقه ۹۰ دقیقه‌ای بین این تیم و حریف. در
        صورتی که مسابقه در مرحله حذفی باشد و پس از ۹۰ دقیقه مساوی
        باشد، وقت اضافه و در صورت لزوم ضربات پنالتی نیز شبیه‌سازی
        می‌شود. در مرحله گروهی، مسابقات مساوی بدون وقت اضافه/پنالتی
        باقی می‌مانند.

        Args:
            opponent (Team): تیم حریف
            is_knockout (bool): آیا این مسابقه در مرحله حذفی است

        Returns:
            tuple: (گل_تیم_خودی, گل_تیم_حریف, برنده مسابقه (Team یا
            None در صورت تساوی گروهی), دیکشنری جزئیات اضافی شامل
            کلیدهای "extra_time" و "penalties")
        """
        details = {"extra_time": False, "penalties": None}

        self_lambda = self.lambda_vs(opponent)
        opp_lambda = opponent.lambda_vs(self)

        self_goals = poisson_sample(self_lambda)
        opp_goals = poisson_sample(opp_lambda)

        winner = None
        if self_goals > opp_goals:
            winner = self
        elif opp_goals > self_goals:
            winner = opponent
        """ بررسي مرحله حذفي"""
        if is_knockout and winner is None:
            # وقت اضافه (۳۰ دقیقه) - لامبدای هر تیم برابر ۰.۳۳ لامبدای اصلی
            details["extra_time"] = True
            et_self_goals = poisson_sample(self_lambda * 0.33)
            et_opp_goals = poisson_sample(opp_lambda * 0.33)
            self_goals += et_self_goals
            opp_goals += et_opp_goals

            if self_goals > opp_goals:
                winner = self
            elif opp_goals > self_goals:
                winner = opponent

            if winner is None:
                # ضربات پنالتی - گل‌های پنالتی جزو گل‌های بازی محسوب نمی‌شوند
                winner, pens = self._simulate_penalties(opponent)
                details["penalties"] = pens

        return self_goals, opp_goals, winner, details

    def _simulate_penalties(self, opponent):
        """
        شبیه‌سازی ضربات پنالتی (۵ ضربه برای هر تیم و در صورت تساوی،
        پنالتی ناگهانی) بین این تیم و حریف.

        Args:
            opponent (Team): تیم حریف

        Returns:
            tuple: (برنده (Team), (تعداد پنالتی گل‌شده خودی, تعداد
            پنالتی گل‌شده حریف))
        """
        self_p = self._penalty_prob_vs(opponent)
        opp_p = opponent._penalty_prob_vs(self)

        self_pens = 0
        opp_pens = 0
        for item in range(5):
            if random.random() < self_p:
                self_pens += 1
            if random.random() < opp_p:
                opp_pens += 1

        winner = None
        if self_pens > opp_pens:
            winner = self
        elif opp_pens > self_pens:
            winner = opponent

        # پنالتی ناگهانی (Sudden Death): هر دور یک ضربه برای هر تیم
        while winner is None:
            self_scored = random.random() < self_p
            opp_scored = random.random() < opp_p
            if self_scored:
                self_pens += 1
            if opp_scored:
                opp_pens += 1
            if self_scored and not opp_scored:
                winner = self
            elif opp_scored and not self_scored:
                winner = opponent
            # اگر هر دو گل زدند یا هر دو گل نزدند، دور بعدی ادامه می‌یابد

        return winner, (self_pens, opp_pens)
