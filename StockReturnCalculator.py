import requests
import datetime


class CompoundReturnCalc:
    def __init__(self, startingPoint, endingPoint, company, monthlyContrib):
        self.startingPoint = datetime.datetime.strptime(startingPoint, "%Y-%m-%d")
        self.endingPoint = datetime.datetime.strptime(endingPoint, "%Y-%m-%d")
        self.company = company
        self.monthlyContrib = monthlyContrib

        self.balance = 0.0
        self.timesInvested = 0
        self.dividentPay = 0.0
        self.dataResponse = {}
        self.metaData = {}
        self.daysTraded = []
        self.divTimestamps = []
        self.companyPaysDividents = False

        self.data = self.getFormattedDataResponse()
        self.calculate()
        return


    def __repr__(self):
        out = "\n"
        out += "{}    -    {:.4f} shares".format(self.company, self.balance) + "\n"
        out += "Time: {} months | {:.2f} years".format(self.timesInvested, self.timesInvested / 12) + "\n"
        out += "______________________________________________________" + "\n\n"
        out += "Total balance: {:.2f} USD".format(self.getTotalValue()) + "\n"
        out += "Money invested: {:.2f} USD".format(self.getInvestedMoney()) + "\n"
        out += "Dividents: {:.2f} USD".format(self.dividentPay) + "\n"
        out += "Earnings: {:.2f} USD ({:.1f}%)".format(self.getEarnings(), self.getEarnings() / self.getInvestedMoney() * 100) + "\n\n"
        out += "Total earnings: {:.2f} USD".format(self.getEarnings() + self.dividentPay) + "\n"
        out += "Total networth: {:.2f} USD".format(self.getTotalValue() + self.dividentPay) + "\n"

        return out


    def getFormattedDataResponse(self):
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{self.company}"
        headers = {'User-Agent': 'FH'}
        params = {
            'period1': int(datetime.datetime.timestamp(self.startingPoint)),
            'period2': int(datetime.datetime.timestamp(self.endingPoint)),
            'interval': '1mo',
            'events': 'div'
        }

        dataResponse = requests.get(
            url = url,
            params = params,
            headers = headers
        )

        return dataResponse.json()["chart"]["result"][0]


    def getTimestampts(self, format):
        if format == 1:
            return self.data["timestamp"]
        return [datetime.datetime.fromtimestamp(x) for x in self.data["timestamp"]]


    def checkForDividents(self):
        try:
            if not self.companyPaysDividents:
                self.divTimestamps = list(map(int, list(self.data["events"]["dividends"].keys())))
            self.companyPaysDividents = True
        except Exception:
            self.companyPaysDividents = False
            return
    
    
    def getDividents(self, currStamp, nextStamp):
        self.checkForDividents()
        div = self.data["events"]["dividends"]
        if self.companyPaysDividents:
            if currStamp <= self.divTimestamps[0] < nextStamp:
                self.dividentPay += (self.balance * div[str(self.divTimestamps[0])]["amount"])
                del self.divTimestamps[0]
        return


    def calculate(self):
        pricesAtOpen = self.data["indicators"]["quote"][0]["open"]
        tradingDays = self.getTimestampts(1)

        for index in range(len(tradingDays)):
            if index < (len(tradingDays) - 1):
                self.getDividents(tradingDays[index], tradingDays[index + 1])
            self.daysTraded += [tradingDays[index]]
            self.balance += (self.monthlyContrib / pricesAtOpen[index])
            self.timesInvested += 1

        return


    def getEarnings(self):
        return (self.balance * self.data["indicators"]["quote"][0]["open"][-1] - self.getInvestedMoney())
    

    def getTotalValue(self):
        return (self.balance * self.data["indicators"]["quote"][0]["open"][-1])
    
    
    def getInvestedMoney(self):
        return self.monthlyContrib * self.timesInvested
    


googleCalc = CompoundReturnCalc("2016-06-15", "2023-06-15", "AAPL", 2000)
print(googleCalc)
