from buying import check_buy_opportunities
from selling import check_sell_opportunities
from trends import check_price_trends as check_trends

def check_price_trends():
    check_trends()
    check_buy_opportunities()
    check_sell_opportunities()
