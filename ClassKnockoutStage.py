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
            round_name (str): نام مرحله (مثلا 'Round of 16')
            matchups (list of tuple): لیست جفت‌های (تیم۱, تیم۲) که
                باید در این مرحله با هم بازی کنند
        """
        self.round_name = round_name
        self.matches = [Match(t1, t2, is_knockout=True) for t1, t2 in matchups]

    def round_play(self):
        """
        اجرای تمام مسابقات این مرحله حذفی.

        Returns:
            None
        """
        for match in self.matches:
            match.play()

    def winners_get(self):
        """
        برگرداندن لیست تیم‌های برنده این مرحله به ترتیب مسابقات، برای
        استفاده در ساخت جفت‌های مرحله بعد.

        Returns:
            list of Team: تیم‌های برنده
        """
        return [match.winner for match in self.matches]

    def results_display(self):
        """
        ساخت رشته متنی خلاصه نتایج تمام مسابقات این مرحله.

        Returns:
            str: خلاصه نتایج مرحله
        """
        lines = ["===== {} =====".format(self.round_name)]
        for match in self.matches:
            lines.append(match.result_str())
        return "\n".join(lines)
