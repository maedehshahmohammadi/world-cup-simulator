# ================================
# دانشجو : مائده شاه محمدي
# شماره دانشجويي : 404130823
# عنوان پروژه: شبیه‌ساز جام جهانی
# تاريخ تحويل : 1405/5/3
# ================================

"""
شبیه‌ساز جام جهانی فوتبال 2026 (World Cup Simulator 2026)
با رویکرد کلاسیک 32 تیمی.
این برنامه تیم هارا از فایل CSV میخواند و طبق سیدبندی فیفا گروه بندی میکند
مراحل حذفی را شبیه سازی میکند . برنده ی جام جهانی را مشخص میکند و همچنین احتمال چندین بار شبیه سازی را داد در پایان درصد احتمال قهرمانی را هم اعلام میکند .

"""

import csv
import os
import random

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def poisson_sample(lam):
    """
    تولید یک عدد صحیح تصادفی بر اساس توزیع پواسون با میانگین lam.

    در صورت وجود کتابخانه numpy از numpy.random.poisson استفاده
    می‌شود (سریع‌تر و بهینه‌تر برای اجرای هزاران شبیه‌سازی). در غیر
    این صورت از یک پیاده‌سازی دستی (الگوریتم Knuth) استفاده می‌شود
    تا برنامه بدون numpy هم به درستی کار کند.
   lam باید مثبت باشد
    """
    if lam <= 0:
        lam = 0.01

    if HAS_NUMPY:
        return int(np.random.poisson(lam=lam))

    # پیاده‌سازی دستی توزیع پواسون (الگوریتم Knuth) در صورت نبود numpy
    l_threshold = pow(2.718281828459045, -lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= random.random()
        if p <= l_threshold:
            return k - 1


class Team:
    """
    کلاس تیم .

    مسئولیت این کلاس نگهداری اطلاعات پایه هر تیم (نام، قدرت حمله و
    دفاع، رتبه فیفا) و آمار آن در طول بازی است (گل زده، گل خورده،
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
        """محاسبه میانگین گل مورد انتظار (لامبدا) این تیم مقابل حریف """
        return (self.attack / 100) * 1.5 + (1 - opponent.defense / 100) * 0.8

    def _penalty_prob_vs(self, opponent):
        """محاسبه احتمال گل شدن یک ضربه پنالتی این تیم مقابل حریف """
        prob = 0.75 + (self.attack - opponent.defense) / 250
        return max(0.6, min(0.9, prob))

    def simulate_match(self, opponent, is_knockout=False):
        """
        شبیه‌سازی نتیجه یک مسابقه ۹۰ دقیقه‌ای بین این تیم و حریف. در
        صورتی که مسابقه در مرحله حذفی باشد و پس از ۹۰ دقیقه مساوی
        باشد، وقت اضافه و در صورت لزوم پنالتی نیز شبیه‌سازی
        می‌شود. در مرحله گروهی، مسابقات مساوی بدون وقت اضافه/پنالتی
        باقی می‌مانند.

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

        # هر دور یک ضربه برای هر تیم
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

        return winner, (self_pens, opp_pens)


class Match():
    """
    کلاس مسابقه بین دو تیم.

    مسئولیت این کلاس اجرای یک مسابقه مشخص (گروهی یا حذفی)، به‌روزرسانی
    آمار تیم‌ها بر اساس نتیجه، و تعیین برنده (در مراحل حذفی) است.
    """

    def __init__(self, team1, team2, is_knockout=False):
        """
            team1 (Team): تیم اول
            team2 (Team): تیم دوم
            is_knockout (bool): آیا مسابقه در مرحله حذفی است
        """
        self.team1 = team1
        self.team2 = team2
        self.goals1 = 0
        self.goals2 = 0
        self.is_knockout = is_knockout
        self.winner = None
        self.details = None

    def play(self):
        """
        انجام مسابقه: محاسبه نتیجه با فراخوانی simulate_match، به‌روزرسانی
        آمار گل هر دو تیم، امتیازدهی (فقط در مرحله گروهی) و تعیین
        برنده (در مراحل حذفی).
        
        """
        g1, g2, winner, details = self.team1.simulate_match(self.team2, self.is_knockout)
        self.goals1 = g1
        self.goals2 = g2
        self.details = details
        self.winner = winner

        self.team1.for_goals += g1
        self.team1.against_goals += g2
        self.team2.for_goals += g2
        self.team2.against_goals += g1

        if not self.is_knockout:
            if g1 > g2:
                self.team1.points += 3
            elif g2 > g1:
                self.team2.points += 3
            else:
                self.team1.points += 1
                self.team2.points += 1

    def result_str(self):
        """
        بازگرداندن نتیجه مسابقه برای نمایش (شامل نتیجه
        پنالتی در صورت وجود و برنده مسابقه در مراحل حذفی).

        Returns:
            str: رشته نتیجه مسابقه
        """
        text = "{} {}-{} {}".format(self.team1.name, self.goals1, self.goals2, self.team2.name)
        if self.details and self.details.get("penalties"):
            p1, p2 = self.details["penalties"]
            text += " ({}-{} pens)".format(p1, p2)
        if self.winner:
            text += " -> برنده: {}".format(self.winner.name)
        return text


class Group:
    """
    کلاس گروه در مرحله گروهی جام جهانی.

    مسئولیت این کلاس نگهداری ۴ تیم یک گروه، اجرای تمام مسابقات درون
    گروهی (هر تیم یک بار با هر تیم دیگر) و رتبه‌بندی نهایی تیم‌ها بر
    اساس امتیاز، تفاضل گل، گل زده و در نهایت قرعه‌کشی تصادفی است.
    """

    def __init__(self, name, teams):
        """
        کلاس گروه.

            name (str): نام گروه (مثلا 'A', 'B', ...)
            teams (list of Team): لیست ۴ تیم عضو گروه
        """
        self.name = name
        self.teams = teams
        self.matches = []

    def matches_all_play(self):
        """
        اجرای تمام مسابقات گروه؛ هر تیم دقیقا یک بار با سه تیم دیگر
        گروه بازی می‌کند (در مجموع ۶ مسابقه برای هر گروه).

        Returns:
             لیست مسابقات انجام‌شده گروه
        """
        self.matches = []
        n = len(self.teams)
        for i in range(n):
            for j in range(i + 1, n):
                match = Match(self.teams[i], self.teams[j], is_knockout=False)
                match.play()
                self.matches.append(match)
        return self.matches
    """مزتب کردن ب ر اساس امتياز تفاضل گل و گل هاي زده شده"""
    def ranking_get(self):
        sorted_teams = sorted(
            self.teams,
            key=lambda team: (
                team.points,          
                team.goal_difference(), 
                team.for_goals         
            ),
            reverse=True  
        )
        
        return sorted_teams
    def advance_teams(self):
        """
        برگرداندن دو تیم اول و دوم گروه که به مرحله حذفی صعود می‌کنند.

        Returns:
            tuple: (تیم اول گروه, تیم دوم گروه)
        """
        ranking = self.ranking_get()
        return ranking[0], ranking[1]

    def table_display(self):
        """
     جدول رده‌بندی گروه برای نمایش به کاربر.
        """
        ranking = self.ranking_get()
        lines = ["===== Group {} =====".format(self.name)]
        for idx, team in enumerate(ranking, start=1):
            lines.append("{}. {}: {} pts, GD {:+d}, GF {}".format(
                idx, team.name, team.points, team.goal_difference(), team.for_goals))
        return "\n".join(lines)


class KnockoutStage:
    """
    کلاس یک مرحله از مراحل حذفی (یک‌هشتم، یک‌چهارم، نیمه‌نهایی، فینال).

    مسئولیت این کلاس نگهداری لیست مسابقات یک مرحله حذفی، اجرای تمام
    آن مسابقات و برگرداندن لیست تیم‌های برنده (که به مرحله بعد
    می‌روند) است.
    """

    def __init__(self, round_name, matchups):
        """
        سازنده کلاس مرحله حذفی.

        Args:
            round_name : نام مرحله (مثلا 'Round of 16')
            matchups (list of tuple): لیست جفت‌های (تیم۱, تیم۲) که
                باید در این مرحله با هم بازی کنند
        """
        self.round_name = round_name
        self.matches = [Match(t1, t2, is_knockout=True) for t1, t2 in matchups]

    def round_play(self):
        """
        اجرای تمام مسابقات این مرحله حذفی.
        """
        for match in self.matches:
            match.play()

    def winners_get(self):
        """
        برگرداندن لیست تیم‌های برنده این مرحله به ترتیب مسابقات

        Returns:
             لیست تیم‌های برنده
        """
        return [match.winner for match in self.matches]

    def results_display(self):
        """
        ساخت رشته متنی خلاصه نتایج تمام مسابقات این مرحله.
        """
        lines = ["===== {} =====".format(self.round_name)]
        for match in self.matches:
            lines.append(match.result_str())
        return "\n".join(lines)


class WorldCupSimulator:
    """
    کلاس اصلی شبیه‌ساز جام جهانی.

    مسئولیت این کلاس هماهنگی کل فرآیند تورنمنت است: خواندن تیم‌ها از
    فایل CSV، قرعه‌کشی گروه‌ها بر اساس سیدبندی فیفا، اجرای مرحله
    گروهی، ساخت براکت حذفی طبق قانون فیفا، اجرای مراحل حذفی تا
    مشخص شدن قهرمان، و همچنین اجرای چندباره کل تورنمنت برای محاسبه
    درصد قهرمانی هر تیم.
    """

    def __init__(self):
        """سازنده کلاس شبیه‌ساز؛ مقداردهی اولیه وضعیت خالی تورنمنت"""
        self.teams = []
        self.groups = []
        self.round_of_16 = None
        self.quarterfinals = None
        self.semifinals = None
        self.final = None
        self.champion = None

    def load_teams_from_csv(self, filename):
        """
        خواندن فایل CSV تیم‌ها و ساخت اشیاء Team متناظر.

        Args:
            filename (str): مسیر/نام فایل CSV (ستون‌ها: name, attack,
                defense, rank)

        Returns:
            bool: True در صورت موفقیت، False در صورت شکست
        """
        if not os.path.exists(filename):
            print("خطا: فایل '{}' یافت نشد.".format(filename))
            return False

        try:
            teams = []
            with open(filename, newline='', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    teams.append(Team(row['name'], row['attack'], row['defense'], row['rank']))

            if not teams:
                print("خطا: فایل CSV خالی است یا ساختار آن نامعتبر است.")
                return False

            if len(teams) != 32:
                print("هشدار: تعداد تیم‌های خوانده‌شده {} است (انتظار می‌رفت 32 تیم باشد).".format(len(teams)))

            self.teams = teams
            print("{} تیم با موفقیت از فایل '{}' بارگذاری شد.".format(len(self.teams), filename))
            return True
        except (KeyError, ValueError) as exc:
            print("خطا: ساختار فایل CSV نامعتبر است ({}).".format(exc))
            return False
        except Exception as exc:
            print("خطا در خواندن فایل: {}".format(exc))
            return False

    def groups_draw_and_seed(self):
        """
        قرعه‌کشی گروه‌ها بر اساس سیدبندی (رنکینگ فیفا). تیم‌ها ابتدا
        بر اساس رتبه به چهار سید تقسیم می‌شوند (سید ۱: رتبه‌های ۱-۸،
        سید ۲: رتبه‌های ۹-۱۶، سید ۳: رتبه‌های ۱۷-۲۴، سید ۴: رتبه‌های
        ۲۵-۳۲). سپس تیم‌های هر سید به‌صورت تصادفی و بدون جایگزینی بین
        هشت گروه توزیع می‌شوند طوری که هر گروه دقیقا یک تیم از هر سید
        داشته باشد.

        Returns:
            bool: True در صورت موفقیت، False در صورت نبود تیم بارگذاری‌شده
        """
        if not self.teams:
            print("ابتدا تیم‌ها را بارگذاری کنید.")
            return False

        sorted_teams = sorted(self.teams, key=lambda t: t.rank)
        pots = [sorted_teams[0:8], sorted_teams[8:16], sorted_teams[16:24], sorted_teams[24:32]]

        group_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        """يک ديگشنري با کليد نام گروه و مقادير ليست خالي که تيم ها درون آن قرار ميگيرد"""
        groups_teams = {name: [] for name in group_names}

        for pot in pots:
            pot_shuffled = pot[:]
            random.shuffle(pot_shuffled)
            names_shuffled = random.sample(group_names, len(group_names))
            for name, team in zip(names_shuffled, pot_shuffled):
                groups_teams[name].append(team)
                team.group = name

        self.groups = [Group(name, groups_teams[name]) for name in group_names]
        print("قرعه‌کشی گروه‌ها با موفقیت انجام شد.")
        return True

    def stage_group_run(self):
        """
        اجرای مرحله گروهی (تمام مسابقات هر گروه) و چاپ جدول رده‌بندی
        هر گروه.

        Returns:
            bool: True در صورت موفقیت، False اگر قرعه‌کشی انجام نشده باشد
        """
        if not self.groups:
            print("ابتدا قرعه‌کشی گروه‌ها را انجام دهید.")
            return False

        for group in self.groups:
            group.matches_all_play()
            print(group.table_display())
        return True

    def bracket_knockout_setup(self):
        """
        ساخت براکت مرحله یک‌هشتم نهایی بر اساس قانون ثابت فیفا:
        A1 vs B2, C1 vs D2, E1 vs F2, G1 vs H2,
        B1 vs A2, D1 vs C2, F1 vs E2, H1 vs G2

        Returns:
            bool: True در صورت موفقیت، False اگر مرحله گروهی هنوز اجرا نشده باشد
        """
        if not self.groups:
            print("ابتدا مرحله گروهی را اجرا کنید.")
            return False

        firsts = {}
        seconds = {}
        for group in self.groups:
            first, second = group.advance_teams()
            firsts[group.name] = first
            seconds[group.name] = second

        pairing = [
            ('A', 'B'), ('C', 'D'), ('E', 'F'), ('G', 'H'),
            ('B', 'A'), ('D', 'C'), ('F', 'E'), ('H', 'G'),
        ]
        matchups = [(firsts[g1], seconds[g2]) for g1, g2 in pairing]
        self.round_of_16 = KnockoutStage('Round of 16', matchups)
        return True

    def stage_knockout_run(self):
        """
        اجرای تمام مراحل حذفی (یک‌هشتم، یک‌چهارم، نیمه‌نهایی، فینال)
        و مشخص کردن قهرمان تورنمنت.

        Returns:
            Team یا None: قهرمان تورنمنت
        """
        if self.round_of_16 is None:
            self.bracket_knockout_setup()
        if self.round_of_16 is None:
            return None

        self.round_of_16.round_play()
        r16_winners = self.round_of_16.winners_get()
        """يک چهارم نهايي"""
        qf_matchups = [(r16_winners[i], r16_winners[i + 1]) for i in range(0, 8, 2)]
        self.quarterfinals = KnockoutStage('Quarterfinals', qf_matchups)
        self.quarterfinals.round_play()
        qf_winners = self.quarterfinals.winners_get()
        """نيمه نهايي"""
        sf_matchups = [(qf_winners[i], qf_winners[i + 1]) for i in range(0, 4, 2)]
        self.semifinals = KnockoutStage('Semifinals', sf_matchups)
        self.semifinals.round_play()
        sf_winners = self.semifinals.winners_get()
        """نهايي"""
        final_matchups = [(sf_winners[0], sf_winners[1])]
        self.final = KnockoutStage('Final', final_matchups)
        self.final.round_play()

        self.champion = self.final.winners_get()[0]
        return self.champion

    def simulation_full_run(self):
        """
        اجرای کامل یک دوره جام جهانی (مرحله گروهی + مراحل حذفی) و
        برگرداندن قهرمان. پیش از شروع، آمار تمام تیم‌ها (امتیاز، گل
        زده و گل خورده) ریست می‌شود تا اجراهای متعدد روی هم اثر
        نگذارند.

        Returns:
            Team: قهرمان این اجرای تورنمنت
        """
        for team in self.teams:
            team.reset_stats()
            team.group = None

        self.groups_draw_and_seed()
        for group in self.groups:
            group.matches_all_play()

        self.bracket_knockout_setup()
        self.stage_knockout_run()
        return self.champion

    def champion_likely_most(self, simulations_num=1000):
        """
        اجرای شبیه‌سازی کامل تورنمنت به تعداد دلخواه (پیش‌فرض ۱۰۰۰
        بار) و محاسبه درصد قهرمانی هر تیم در کل اجراها.

        Args:
            simulations_num (int): تعداد دفعات اجرای کامل تورنمنت

        Returns:
            dict یا None: دیکشنری {نام تیم: درصد قهرمانی} یا None در
            صورت بروز خطا
        """
        if simulations_num <= 0:
            print("خطا: تعداد شبیه‌سازی باید عددی مثبت باشد.")
            return None
        if not self.teams:
            print("ابتدا تیم‌ها را بارگذاری کنید.")
            return None

        counts = {team.name: 0 for team in self.teams}
        for _ in range(simulations_num):
            champion = self.simulation_full_run()
            counts[champion.name] += 1

        print("شبیه‌سازی {} بار انجام شد.".format(simulations_num))
        print("درصد قهرمانی هر تیم:")
        percentages = {}
        for name, count in sorted(counts.items(), key=lambda item: -item[1]):
            pct = (count / simulations_num) * 100
            percentages[name] = pct
            if pct > 0:
                print("{}: {:.1f}%".format(name, pct))
        return percentages

    def bracket_display(self):
        """
        نمایش براکت حذفی کامل مربوط به آخرین شبیه‌سازی انجام‌شده.

        Returns:
            None
        """
        if self.round_of_16 is None:
            print("هنوز هیچ شبیه‌سازی حذفی انجام نشده است.")
            return

        print("===== Knockout Bracket =====")
        print(self.round_of_16.results_display())
        if self.quarterfinals:
            print(self.quarterfinals.results_display())
        if self.semifinals:
            print(self.semifinals.results_display())
        if self.final:
            print(self.final.results_display())
        if self.champion:
            print("Champion: {}".format(self.champion.name))


def print_menu():
    """چاپ منوی اصلی برنامه"""
    print("""
===== شبیه‌ساز جام جهانی =====
1) بارگذاری تیم‌ها از فایل CSV
2) انجام قرعه‌کشی گروه‌ها (سیدبندی خودکار)
3) اجرای مرحله گروهی و نمایش جدول هر گروه
4) اجرای کامل جام (گروهی + حذفی) و نمایش قهرمان
5) شبیه‌سازی 1000 باره و گزارش درصد قهرمانی
6) نمایش براکت حذفی آخرین شبیه‌سازی
7) خروج
""")


def main():
    """حلقه اصلی برنامه و مدیریت منو"""
    simulator = WorldCupSimulator()
    default_filename = "t1.csv"

    while True:
        print_menu()
        choice = input("گزینه مورد نظر را انتخاب کنید: ").strip()

        if choice == '1':
            entered = input("نام فایل CSV را وارد کنید (خالی بگذارید برای '{}'): ".format(default_filename)).strip()
            filename = entered if entered else default_filename
            simulator.load_teams_from_csv(filename)

        elif choice == '2':
            if not simulator.teams:
                print("ابتدا تیم‌ها را بارگذاری کنید.")
                continue
            simulator.groups_draw_and_seed()

        elif choice == '3':
            if not simulator.groups:
                print("ابتدا قرعه‌کشی گروه‌ها را انجام دهید.")
                continue
            simulator.stage_group_run()

        elif choice == '4':
            if not simulator.teams:
                print("ابتدا تیم‌ها را بارگذاری کنید.")
                continue
            champion = simulator.simulation_full_run()
            simulator.bracket_display()
            if champion:
                print("قهرمان جام جهانی: {}".format(champion.name))

        elif choice == '5':
            if not simulator.teams:
                print("ابتدا تیم‌ها را بارگذاری کنید.")
                continue
            entered = input("تعداد شبیه‌سازی را وارد کنید (خالی بگذارید برای 1000): ").strip()
            num_simulations = 1000
            if entered:
                try:
                    num_simulations = int(entered)
                except ValueError:
                    print("خطا: عدد وارد شده نامعتبر است.")
                    continue
            simulator.champion_likely_most(num_simulations)

        elif choice == '6':
            if not simulator.teams:
                print("ابتدا تیم‌ها را بارگذاری کنید.")
                continue
            simulator.bracket_display()

        elif choice == '7':
            print("خدانگهدار!")
            break

        else:
            print("گزینه نامعتبر است، لطفا دوباره تلاش کنید.")



if __name__ == '__main__':
    main()