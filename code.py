# ------------------------------------------------------------------------------------------------------------------------------------------
#                                   Use the following command to run the code: python3 code.py > output.txt
# ------------------------------------------------------------------------------------------------------------------------------------------
import json

# The following code assumed that tokenized stocks are not present, therefore stocks can only be integers.

# opening the input.json file. Make sure the file is in the same directory as the code.py
with open('input.json') as json_file:
    data = json.load(json_file)
    actions = data['actions']
    stock_actions = data['stock_actions']

traderActions = actions + stock_actions

# The following is a Portfolio of stocks a perticular trader owns


class Portfolio:
    # The following initilizes a Portfolio object while begining the code
    def __init__(self):
        # Initializing a list of stocks
        self.stocks = []
        # Divident income literal assigned to 0 initially
        self.dividendIncomeRecieved = "0"

     # Retuns the stock dict passed if the stockName exists
    def getStock(self, stockName):
        for s in self.stocks:
            if s['stock'] == stockName:
                return s
        return None

    # The following is function is used when trader buys a stock. Arguments are Portfolio, stockName, shares previously availble (=0 initiallly), Previous price (=0 initially)
    # We return the type of action that was performed, i.e Buying the stock or adding onto the position
    def buyStock(self, stockName, shares, price):
        # If the stock is not found, we create a stockToBuy dictionary and store the data accordingly, then we finally append the dictionary to the Portfolio.
        if self.getStock(stockName) is None:
            stockToBuy = {}
            stockToBuy['stock'] = stockName
            stockToBuy['shares'] = shares
            stockToBuy['value'] = "{0:.2f}".format(float(price))
            self.stocks.append(stockToBuy)
        # If the stock is found, we do the required math and calacute average price, total shares.
        else:
            stockToBuy = self.getStock(stockName)
            stockToBuy['value'] = "{0:.2f}".format((((float(stockToBuy['value']) * int(stockToBuy['shares'])) + (
                float(price) * int(shares))) / (int(stockToBuy['shares']) + int(shares))))
            stockToBuy['shares'] = str(
                int(stockToBuy['shares']) + int(shares))
        return "You bought {shares} shares of {stock} at a price of ${price:.2f} per share".format(
            shares=shares,
            stock=stockName,
            price=float(price)
        )

    # Selling a stock, Arguments are Portfolio, stockName, shares to sell and price to sell at
    # We return the transaction to keep track of while printing the summary of the trader.
    def sellStock(self, stockName, shares, price):
        # The following code is pretty much math and self explanatory
        stockToSell = self.getStock(stockName)
        stockToSell['shares'] = str(
            int(stockToSell['shares']) - int(shares))
        transactionBal = (
            float(price) - float(stockToSell['value'])) * int(shares)
        result = "loss" if (transactionBal < 0) else "profit"
        return "You sold {share} shares of {stock} at a price of ${price:.2f} per share for a {res} of ${transBal:.2f}".format(
            share=shares,
            stock=stockName,
            price=float(price),
            res=result,
            transBal=transactionBal
        )

    # A split stock function that takes in Portfolio, stockName and split ratio
    # Returns a string similar to other transactional functions of the action that we just did
    def splitStock(self, stockName, split):

        stockBeingSplit = self.getStock(stockName)
        stockBeingSplit['shares'] = str(
            int(stockBeingSplit['shares']) * int(split))
        stockBeingSplit['value'] = "{0:.2f}".format(
            (float(stockBeingSplit['value']) / int(split)))
        return "{stock} split {split} to 1, and you have {sharesOfStockBeingSplit} shares".format(
            stock=stockName,
            split=split,
            sharesOfStockBeingSplit=stockBeingSplit['shares']
        )

    # A function that pays dividends to the user. Arguments are Portfolio, stockName and dividend recieved.
    # returns a string for the action performed if dividend payment was successful.
    def payDividends(self, stockName, dividend):

        stockPayingDividends = self.getStock(stockName)
        self.dividendIncomeRecieved = "{0:.2f}".format(float(
            self.dividendIncomeRecieved) + int(stockPayingDividends['shares']) * float(dividend))
        return "{stock} paid out ${div:.2f} dividend per share, and you have {sharesOfStockPaysDiv} shares".format(
            stock=stockName,
            sharesOfStockPaysDiv=stockPayingDividends['shares'],
            div=float(dividend)
        )

    # Tries to execute a action by the trader, we use actions dict we initilized in the begening
    # This function does the hard work of determining wether to buy, sell, pay dividend or split a stock.
    # This then calls the funcion accordingly. Action is a trader action or stockAction

    def executeAction(self, action):

        if action in actions:
            if action['action'] == 'BUY':
                return self.buyStock(action['ticker'], action['shares'], action['price'])
            else:
                return self.sellStock(action['ticker'], action['shares'], action['price'])
        else:
            if(action['dividend'] != ''):
                return self.payDividends(action['stock'], action['dividend'])
            else:
                return self.splitStock(action['stock'], action['split'])

    # Checks if a proposed transaction is valid. Ex: Checks if the stock exists before payment of dividends. Returns a
    # bool if it is a valid transaction.
    def validTransaction(self, action):

        stockInPortfolio = False
        if action in actions:
            if action['action'] == 'SELL':
                for s in self.stocks:
                    if s['stock'] == action['ticker']:
                        stockInPortfolio = True
                if not stockInPortfolio:
                    return False
                if int(action['shares']) > int(self.getStock(action['ticker'])['shares']):
                    return False
        else:
            for s in self.stocks:
                if s['stock'] == action['stock']:
                    stockInPortfolio = True
            if not stockInPortfolio:
                return False
        return True

    # Function to print the portolio to the terminal, this could be piped to an output file
    def printPortfolio(self, date):

        print("On " + date.replace('/', '-') + ", you have:")
        for stock in self.stocks:
            if stock['shares'] != 0:
                print("    - " + stock['shares'] + " shares of " +
                      stock['stock'] + " at $" + stock['value'] + " per share")
        print("    - $" + str(self.dividendIncomeRecieved) + " of dividend income")

    # generate statement generates the report of stocks the trader owns, takes Portfolio as an argument
    # Prints the transactions
    def generateStatement(self):
        # List to store all the dates
        dates = []
        for iter in traderActions:
            if iter['date'][0:10] not in dates:
                dates.append(iter['date'][0:10])
        dates.sort()
        for d in dates:
            dailyActionss = self.getDailyTransactions(d)

            # A list to record transactions that trader did in Buy and Sell
            transactionRecords = []
            if dailyActionss:
                for a in dailyActionss:
                    if self.validTransaction(a):
                        transactionRecords.append(self.executeAction(a))

            # Remove companies whose stocks are =0
            for stock in self.stocks:
                if stock['shares'] == '0':
                    self.stocks.remove(stock)
            if transactionRecords:
                self.printPortfolio(d)
                print("  Transactions:")
                for record in transactionRecords:
                    print("    - " + record)

    # A list to take care of transactions happening on a perticualr date.
    def getDailyTransactions(self, date):

        dailyActionss = []
        for a in traderActions:
            if a['date'].startswith(date):
                dailyActionss.append(a)
        return dailyActionss


# in main
if __name__ == '__main__':
    # Initializing a portfolio object
    p = Portfolio()
    # Generating the stock statement
    p.generateStatement()
