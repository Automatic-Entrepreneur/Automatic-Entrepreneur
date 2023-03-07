import pandas as pd
import json

def generate_table(GD_data):
    return_df = pd.DataFrame()
    for dic in GD_data['Balance Sheet']:
        for k, v in dic.keys():
            if dic[k] == None:
                dic[k] = 0
        dic.update((k, int(dic[k])/1000000) for k, v in dic.items() if k in ['totalAssets', 
                   'investments', 
                   'totalLiabilities', 
                   'deferredRevenue', 
                   'currentDebt'])
    for dic in GD_data['Income Statement']:
        for k, v in dic.keys():
            if dic[k] == None:
                dic[k] = 0
        dic.update((k, int(dic[k])/1000000) for k, v in dic.items() if k in ['researchAndDevelopment', 
                    'ebitda', 
                    'grossProfit', 
                    'totalRevenue', 
                    'netIncome'])
    for dic in GD_data['Cash Flow']:
        for k, v in dic.keys():
            if dic[k] == None:
                dic[k] = 0
        dic.update((k, int(dic[k])/1000000) for k, v in dic.items() if k in ['operatingCashflow', 
                        'profitLoss'])
    for dic in GD_data['Annual Earnings']:
        for k, v in dic.keys():
            if dic[k] == None:
                dic[k] = 0
        dic.update((k, int(dic[k])/1000000) for k, v in dic.items())
    for i in ['Balance Sheet', 'Income Statement', 'Cash Flow', 'Annual Earnings']:
        x = pd.DataFrame(GD_data[i])
        '''res = [json.loads(idx.replace("'", '"')) for idx in [x]]
        for j in res:
            newlist = j
        x = pd.DataFrame(newlist)'''
        if i == 'Balance Sheet':
            x = x[['fiscalDateEnding', 
                'totalAssets', 
                'investments', 
                'totalLiabilities', 
                'deferredRevenue', 
                'currentDebt']]
        elif i == 'Income Statement':
            x = x[['fiscalDateEnding',
                'reportedCurrency', 
                'researchAndDevelopment', 
                'ebitda', 
                'grossProfit', 
                'totalRevenue', 
                'netIncome']]
        elif i == 'Cash Flow':
            x = x[['fiscalDateEnding', 
                    'operatingCashflow', 
                    'profitLoss']]
        elif i == 'Annual Earnings':
            x = x.loc[:5]
            
        # Set datetime
        x['fiscalDateEnding'] = pd.to_datetime(x['fiscalDateEnding'])
        
        # Merge dataframes
        if return_df.empty:
            return_df = x
        else:
            return_df = return_df.merge(x, on = 'fiscalDateEnding')
            
    # Rename Columns
    return_df = return_df.rename(columns = {'fiscalDateEnding' : 'FY', 
                                'reportedEPS' : 'EPS', 
                                'grossProfit' : 'Gross Profit (M)', 
                                'totalRevenue' : 'Revenue (M)', 
                                'ebitda' : 'EBITDA (M)', 
                                'netIncome' : 'Net Income (M)', 
                                'totalAssets' : 'Assets (M)', 
                                'investments' : 'Investments (M)', 
                                'totalLiabilities' : 'Liabilities (M)', 
                                'deferredRevenue' : 'Deferred Revenue (M)', 
                                'currentDebt' : 'Current Debt (M)', 
                                'operatingCashflow' : 'Operating Cash Flow (M)', 
                                'profitLoss' : 'Profit Loss (M)', 
                                'reportedCurrency' : 'Currency', 
                                'researchAndDevelopment' : 'R&D (M)'})
    # temporarily set None to 0
    #return_df = return_df.replace('None', 0)

    # set financial year
    return_df['FY'] = pd.DatetimeIndex(return_df['FY']).year

    mils = ['Gross Profit (M)', 
            'Revenue (M)', 
            'Net Income (M)', 
            'Assets (M)', 
            'Investments (M)', 
            'Liabilities (M)', 
            'Current Debt (M)', 
            'Deferred Revenue (M)', 
            'Operating Cash Flow (M)', 
            'Profit Loss (M)', 
            'EBITDA (M)', 
            'R&D (M)']
    return_df[mils] = return_df[mils].astype(int)
    return_df['EPS'] = return_df['EPS'].astype(float)
    pd.options.display.float_format = '{:,.2f}'.format
    return_df['EPS'] = return_df['EPS'].astype(str)

    '''
    # convert to millions
    for i in mils:
        return_df[i] = return_df[i]/1000000
        return_df[[i]] = return_df[[i]].astype(int)'''
        
    # replace 0s
    return_df = return_df.replace(0, 'N/A')

    # set order
    return_df = return_df[['FY', 'Currency', 'EPS'] + mils]

    # export to html
    n = return_df.to_html(index = False)
    n = n.replace('<tr>', '<tr align="center">')
    n = n.replace('<th>', '<th align="center">')
    n = n.replace('border="1"', 'border="1" style = "border-collapse: collapse;"')
    return n