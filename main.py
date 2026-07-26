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

from ClassTeam import Team
from ClassMatch import Match
from ClassGroup import Group
from ClassKnockoutStage import KnockoutStage
from worldcup_simulator import WorldCupSimulator

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