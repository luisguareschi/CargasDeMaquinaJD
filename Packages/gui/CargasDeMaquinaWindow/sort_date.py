import datetime as dt
import dateutil.parser


def sort_list_by_date(all_dates_list: list) -> list:
    new_list = []
    while all_dates_list:
        minimum: str = all_dates_list[0]
        m = minimum + minimum[3:]
        minimum_dt = dateutil.parser.parse(m, yearfirst=True, dayfirst=False)
        for x in all_dates_list:
            xx = x + x[3:]
            x_dt = dateutil.parser.parse(xx, yearfirst=True, dayfirst=False)
            if x_dt < minimum_dt:
                minimum_dt = x_dt
                minimum = x
        new_list.append(minimum)
        all_dates_list.remove(minimum)
    return new_list


if __name__ == '__main__':
    l = ['Jan-23', 'Feb-23', 'Mar-23', 'Apr-23', 'May-23', 'Jun-23', 'Jul-23', 'Aug-23', 'Sep-23', 'Oct-23', 'Nov-22',
         'Dec-22']
    l = sort_list_by_date(l)
    print(l)
