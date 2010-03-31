import tables as pt
from models.PositionModel import PositionModel
'''
Based on the model:
PositionModel:
    timestamp = pt.Time64Col()
    symbol = pt.StringCol(4) 
    shares = pt.Int32Col()
    open_price = pt.Int32Col()
'''

class Position:
    def __init__(self):
        self.positionFile = pt.openFile('PositionModel.h5', mode = "w")
        self.position = self.positionFile.createTable('/', 'position', PositionModel)

    def addPosition(self,timestamp,symbol,shares,open_price):
        print 'RUNNING ADD POS'
        row = self.position.row
        row['timestamp'] = timestamp
        row['symbol'] = symbol 
        row['shares'] = shares
        row['open_price'] = open_price
        row.append()
        self.position.flush()
    
    def removePosition(self, symbol, shares, closeType):
        '''
        symbol: the representation of the shares to be removed
        shares: the number of shares to remove
        closeType: removal order "lifo" or "fifo"
        Removes/modifies positions until the total number of shares have been removed
        NOTE: Method assumes that verification of valid sell has already been completed
        '''
        rows = []
        print 'REMOVING POSITIONS'
        for row in self.position.iterrows():
            print 'ROW:', row
        for row in self.position.where("symbol==%s"%symbol):
            print row
            rows.append(self.cloneRow(row))
        if(closeType=='fifo'):
            i = 0
            row = rows[i]
            posShares = row['shares']            
            while(shares>posShares):
                shares-=posShares
                i+=1
                row = rows[i]
                posShares = row['shares']
            self.position.removeRows(0,i)
            self.position.flush()
            for row in self.position.iterrows(0,1):
                newShares = posShares-shares
                row['shares'] = newShares
                row.update()
            self.position.flush()
                
        elif(closeType=='lifo'):
            i = len(rows)-1
            row = rows[i]
            posShares = row['shares']            
            while(shares>posShares):
                shares-=posShares
                i-=1
                row = rows[i]
                posShares = row['shares']
            self.position.removeRows(i+1,len(rows))
            self.position.flush()
            for row in self.position.iterrows(i,i+1):
                newShares = posShares-shares
                row['shares'] = newShares
                row.update()
            self.position.flush()
        else:
            #invalid type
            raise TypeError("Not an existing close type '%s'." % str(newOrder.order_type))
  
    def cloneRow(self,row):
        dct = {}  
        dct['timestamp'] = row['timestamp']
        dct['symbol'] = row['symbol']
        dct['shares'] = row['shares']
        dct['open_price'] = row['open_price']     
        return dct
    
    def close(self):
        self.positionFile.close()
