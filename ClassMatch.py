class Match():
    """
    کلاس مسابقه بین دو تیم.

    مسئولیت این کلاس اجرای یک مسابقه مشخص (گروهی یا حذفی)، به‌روزرسانی
    آمار تیم‌ها بر اساس نتیجه، و تعیین برنده (در مراحل حذفی) است.
    """

    def __init__(self, team1, team2, is_knockout=False):
        """
        سازنده کلاس مسابقه.

        Args:
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

        Returns:
            None
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
        بازگرداندن رشته متنی نتیجه مسابقه برای نمایش (شامل نتیجه
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
