# coding: utf-8
""" Unit tests for issue 106 reproduction """

import unittest
import xml.etree.ElementTree as ET
import decimal
import datetime

from ibflex import Types, parser, enums

class TradeInitialInvestmentTestCase(unittest.TestCase):
    """Test case for Trade.initialInvestment as boolean field.

    Tests the fix for https://github.com/vroonhof/opensteuerauszug/issues/106
    where initialInvestment="Yes" was causing parsing errors.
    """
    # Sample from the issue
    data = ET.fromstring(
        ('<Trade accountId="accountId" acctAlias="" model="" currency="USD" fxRateToBase="0.82941" '
         'assetCategory="STK" subCategory="ETF" symbol="VT" description="VANGUARD TOT WORLD STK ETF" '
         'conid="52197301" securityID="US9220427424" securityIDType="ISIN" cusip="922042742" '
         'isin="US9220427424" figi="BBG000GM5FZ6" listingExchange="ARCA" underlyingConid="" '
         'underlyingSymbol="VT" underlyingSecurityID="" underlyingListingExchange="" issuer="" '
         'issuerCountryCode="US" tradeID="tradeID" multiplier="1" relatedTradeID="" strike="" '
         'reportDate="20250501" expiry="" dateTime="20250501;155425" putCall="" tradeDate="20250501" '
         'principalAdjustFactor="" settleDateTarget="20250502" transactionType="ExchTrade" '
         'exchange="IBRECINV" quantity="9.2333" tradePrice="117.51" tradeMoney="1084.99498177" '
         'proceeds="-1084.99498177" taxes="0" ibCommission="-0.352528642" ibCommissionCurrency="USD" '
         'netCash="-1085.347510412" closePrice="117.02" openCloseIndicator="O" notes="RI" '
         'cost="1085.347510412" fifoPnlRealized="0" mtmPnl="-4.5142" origTradePrice="0" '
         'origTradeDate="" origTradeID="" origOrderID="0" origTransactionID="0" buySell="BUY" '
         'clearingFirmID="" ibOrderID="ibOrderID" transactionID="redacted" ibExecID="ibExecID" '
         'relatedTransactionID="" rtn="" brokerageOrderID="" orderReference="" volatilityOrderLink="" '
         'exchOrderId="N/A" extExecID="extExecID" orderTime="20250501;092946" openDateTime="" '
         'holdingPeriodDateTime="" whenRealized="" whenReopened="" levelOfDetail="EXECUTION" '
         'changeInPrice="0" changeInQuantity="0" orderType="" traderID="" isAPIOrder="N" '
         'accruedInt="0" initialInvestment="Yes" positionActionID="" serialNumber="" '
         'deliveryType="" commodityType="" fineness="0.0" weight="0.0" />')
    )

    def testParse(self):
        instance = parser.parse_data_element(self.data)
        self.assertIsInstance(instance, Types.Trade)
        self.assertEqual(instance.accountId, "accountId")
        self.assertEqual(instance.currency, "USD")
        self.assertEqual(instance.assetCategory, enums.AssetClass.STOCK)
        self.assertEqual(instance.symbol, "VT")
        self.assertEqual(instance.initialInvestment, True)
        self.assertEqual(instance.quantity, decimal.Decimal("9.2333"))


class EquitySummaryLiteSurchargeAccrualsTestCase(unittest.TestCase):
    """Test case for EquitySummaryByReportDateInBase.liteSurchargeAccruals field.

    Tests the fix for https://github.com/vroonhof/opensteuerauszug/issues/106
    where liteSurchargeAccruals attribute was missing.
    """
    data = ET.fromstring(
        ('<EquitySummaryByReportDateInBase accountId="U123456" '
         'reportDate="2024-01-01" cash="1000.00" total="1000.00" '
         'liteSurchargeAccruals="5.50" />')
    )

    def testParse(self):
        instance = parser.parse_data_element(self.data)
        self.assertIsInstance(instance, Types.EquitySummaryByReportDateInBase)
        self.assertEqual(instance.accountId, "U123456")
        self.assertEqual(instance.reportDate, datetime.date(2024, 1, 1))
        self.assertEqual(instance.cash, decimal.Decimal("1000.00"))
        self.assertEqual(instance.total, decimal.Decimal("1000.00"))
        self.assertEqual(instance.liteSurchargeAccruals, decimal.Decimal("5.50"))

if __name__ == '__main__':
    unittest.main()
