import pandas as pd
import json


def generate_table(GD_data):
    bs_keys = ['totalAssets',
      'investments', 
      'totalLiabilities', 
      'deferredRevenue',
      'currentDebt']
    is_keys = ['researchAndDevelopment', 
            'ebitda', 
            'grossProfit', 
            'totalRevenue', 
            'netIncome']
    cf_keys = ['operatingCashflow', 
            'profitLoss']

    return_df = pd.DataFrame()
        
    for i in ['Balance Sheet', 'Income Statement', 'Cash Flow', 'Annual Earnings']:
        x = pd.DataFrame(GD_data[i])
        '''res = [json.loads(idx.replace("'", '"')) for idx in [x]]
        for j in res:
            newlist = j
        x = pd.DataFrame(newlist)'''
        if i == 'Balance Sheet':
            lst = []
            for d in GD_data[i]:
                dic = {key: d[key] for key in (['fiscalDateEnding'] 
                                               + bs_keys)}
                for k, v in dic.items():
                        if v == 'None':
                            dic[k] = 0
                dic.update((k, int(dic[k])/1000000) for k, v in dic.items() if k in bs_keys)
                lst.append(dic)
            x = pd.DataFrame(lst)
        elif i == 'Income Statement':
            lst = []
            for d in GD_data[i]:
                dic = {key: d[key] for key in (['fiscalDateEnding',
                                               'reportedCurrency'] 
                                               + is_keys)}
                for k, v in dic.items():
                        if v == 'None':
                            dic[k] = 0
                dic.update((k, int(dic[k])/1000000) for k, v in dic.items() if k in is_keys)
                lst.append(dic)
            x = pd.DataFrame(lst)
        elif i == 'Cash Flow':
            lst = []
            for d in GD_data[i]:
                dic = {key: d[key] for key in (['fiscalDateEnding'] 
                                                + cf_keys)}
                for k, v in dic.items():
                        if v == 'None':
                            #print(k)
                            dic[k] = 0
                dic.update((k, int(dic[k])/1000000) for k, v in dic.items() if k in cf_keys)
                lst.append(dic)
            x = pd.DataFrame(lst)
        elif i == 'Annual Earnings':
            count = 0
            lst = []
            for d in GD_data[i]:
                if count < 5:
                    for k, v in d.items():
                            if v == 'None':
                                #print(k)
                                d[k] = 0
                    count += 1
                    lst.append(d)
            x = pd.DataFrame(lst)
            
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