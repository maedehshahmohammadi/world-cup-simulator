class Group:
    """
    کلاس گروه در مرحله گروهی جام جهانی.

    مسئولیت این کلاس نگهداری ۴ تیم یک گروه، اجرای تمام مسابقات درون
    گروهی (هر تیم یک بار با هر تیم دیگر) و رتبه‌بندی نهایی تیم‌ها بر
    اساس امتیاز، تفاضل گل، گل زده و در نهایت قرعه‌کشی تصادفی است.
    """

    def __init__(self, name, teams):
        """
        سازنده کلاس گروه.

        Args:
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
            list of Match: لیست مسابقات انجام‌شده گروه
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
        ساخت رشته متنی جدول رده‌بندی گروه برای نمایش به کاربر.

        Returns:
            str: جدول رده‌بندی گروه
        """
        ranking = self.ranking_get()
        lines = ["===== Group {} =====".format(self.name)]
        for idx, team in enumerate(ranking, start=1):
            lines.append("{}. {}: {} pts, GD {:+d}, GF {}".format(
                idx, team.name, team.points, team.goal_difference(), team.for_goals))
        return "\n".join(lines)
