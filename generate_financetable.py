import pandas as pd
import json


def generate_table(GD_data):
    bs_keys =  ['totalAssets',
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

    lst = []
    for di in GD_data['Balance Sheet']:
        dic = {key: di[key] for key in (['fiscalDateEnding'] 
                                       + bs_keys)}
        for k, v in dic.items():
            if v == 'None':
                dic[k] = 0
        dic.update((k, int(dic[k])/1000000) for k, v in dic.items() if k in bs_keys)
        lst.append(dic)
    bs_df = pd.DataFrame(lst)

    lst = []
    for di in GD_data['Income Statement']:
        dic = {key: di[key] for key in (['fiscalDateEnding',
                                       'reportedCurrency'] 
                                       + is_keys)}
        for k, v in dic.items():
            if v == 'None':
                dic[k] = 0
        dic.update((k, int(dic[k])/1000000) for k, v in dic.items() if k in is_keys)
        lst.append(dic)
    is_df = pd.DataFrame(lst)

    lst = []
    for di in GD_data['Cash Flow']:
        dic = {key: di[key] for key in (['fiscalDateEnding'] + cf_keys)}
        for k, v in dic.items():
            if v == 'None':
                dic[k] = 0
        dic.update((k, int(dic[k])/1000000) for k, v in dic.items() if k in cf_keys)
        lst.append(dic)
    cf_df = pd.DataFrame(lst)

    count = 0
    lst = []
    for di in GD_data['Annual Earnings']:
        if count < 5:
            for k, v in di.items():
                if v == 'None':
                    di[k] = 0
            count += 1
            lst.append(di)
    ae_df = pd.DataFrame(lst)

    # Set datetime
    bs_df['fiscalDateEnding'] = pd.to_datetime(bs_df['fiscalDateEnding'])
    is_df['fiscalDateEnding'] = pd.to_datetime(is_df['fiscalDateEnding'])
    cf_df['fiscalDateEnding'] = pd.to_datetime(cf_df['fiscalDateEnding'])
    ae_df['fiscalDateEnding'] = pd.to_datetime(ae_df['fiscalDateEnding'])

    # Merge dataframes
    return_df = bs_df.merge(is_df, on = 'fiscalDateEnding')
    return_df = return_df.merge(cf_df, on = 'fiscalDateEnding')
    return_df = return_df.merge(ae_df, on = 'fiscalDateEnding')

    # Rename Columns
    return_df = return_df.rename(columns={
        'fiscalDateEnding': 'FY',
        'reportedEPS': 'EPS',
        'grossProfit': 'Gross Profit (M)',
        'totalRevenue': 'Revenue (M)',
        'ebitda': 'EBITDA (M)',
        'netIncome': 'Net Income (M)',
        'totalAssets': 'Assets (M)',
        'investments': 'Investments (M)',
        'totalLiabilities': 'Liabilities (M)',
        'deferredRevenue': 'Deferred Revenue (M)',
        'currentDebt': 'Current Debt (M)',
        'operatingCashflow': 'Operating Cash Flow (M)',
        'profitLoss': 'Profit Loss (M)',
        'reportedCurrency': 'Currency',
        'researchAndDevelopment': 'R&D (M)'})
    
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