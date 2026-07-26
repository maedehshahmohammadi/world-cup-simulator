
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
