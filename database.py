import pandas as pd

# Nhập dữ liệu thô của các quốc gia trên thế giới:
## Biến phụ thuộc:
trade = pd.read_excel('./TRADE.xlsx')

## Biến độc lập chính:
cc = pd.read_excel('./CC.xlsx', sheet_name='Estimate')
ge = pd.read_excel('./GE.xlsx', sheet_name='Estimate')
pv = pd.read_excel('./PV.xlsx', sheet_name='Estimate')
rl = pd.read_excel('./RL.xlsx', sheet_name='Estimate')
rq = pd.read_excel('./RQ.xlsx', sheet_name='Estimate')
va = pd.read_excel('./VA.xlsx', sheet_name='Estimate') 

## Biến kiểm soát:
gdp = pd.read_excel('./GDP.xlsx')
pop = pd.read_excel('./POPULATION.xlsx')
dist = pd.read_excel('./DIST_CONTIG.xlsx')
exrate = pd.read_excel('./NER.xlsx')

## Danh sách các quốc gia quan sát:
ctr = pd.read_excel('./CO.xlsx')



# Tạo bảng dữ liệu thông tin các quốc gia quan sát:
range_year = [*range(2010, 2022, 1)]
year = [str(y) for y in range_year]
n_year = int(len(year))

dict_lst = {'Country_Name': [], 'Counterpart_Country_Name':[], 
            'Country_IMF': [], 'Counterpart_Country_IMF':[], 
            'Country_ISO': [], 'Counterpart_Country_ISO':[]}
ctr_name = ctr['Country'].to_list()
ctr_imf = ctr['IMF_Code'].to_list()
ctr_iso = ctr['ISO_Code'].to_list()

for i in ctr_name:
    for j in ctr_name:
        if i != j:
            dict_lst['Country_Name'].append(i)
            dict_lst['Counterpart_Country_Name'].append(j)

for i in ctr_imf:
    for j in ctr_imf:
        if i != j:
            dict_lst['Country_IMF'].append(i)
            dict_lst['Counterpart_Country_IMF'].append(j)

for i in ctr_iso:
    for j in ctr_iso:
        if i != j:
            dict_lst['Country_ISO'].append(i)
            dict_lst['Counterpart_Country_ISO'].append(j)

df = pd.DataFrame(dict_lst)
df = pd.concat([df]*n_year).sort_values(['Country_ISO', 'Counterpart_Country_ISO']).reset_index(drop=True)
df['Year'] = year*int(len(df)/n_year) # Bảng dữ liệu thông tin các quốc gia quan sát theo thời gian (2)
df_vn = df.loc[df.Country_ISO == "VNM", :].reset_index(drop=True)
df_vn['Year'] = df_vn['Year'].astype('int64')



# Thương mại song phương (Tij):
## Xử lý dữ liệu thô:
melt_trade = pd.melt(trade, id_vars=['Country_IMF', 'Counterpart_Country_IMF'], var_name='Year', value_name='Trade')
melt_trade['Trade'] = melt_trade['Trade'].astype('float64')
melt_trade['Year'] = melt_trade['Year'].astype('int64')

## Gộp dữ liệu thương mại song phương vào bảng dữ liệu chính:
data_nckh = pd.merge(df_vn, melt_trade, how='left', 
                     left_on=['Year', 'Country_IMF', 'Counterpart_Country_IMF'], 
                     right_on=['Year', 'Country_IMF', 'Counterpart_Country_IMF']) # Gộp dữ liệu nhập khẩu vào bảng dữ liệu thông tin các quốc gia quan sát (1)

data_nckh = pd.merge(data_nckh, melt_trade, how='left', 
                     left_on=['Year', 'Country_IMF', 'Counterpart_Country_IMF'], 
                     right_on=['Year', 'Counterpart_Country_IMF', 'Country_IMF'])

data_nckh.loc[:, ['Trade_x','Trade_y']] = data_nckh.loc[:, ['Trade_x','Trade_y']].fillna(0)
data_nckh['Tij'] = data_nckh['Trade_x'] + data_nckh['Trade_y']
data_nckh = data_nckh.drop(labels=['Country_IMF_y', 'Counterpart_Country_IMF_y', 'Trade_x','Trade_y'], axis=1)
data_nckh.columns = data_nckh.columns.str.replace('_x', '')


# Thêm các biến độc lập khác:
## GDP:
def melt_data(variable, name):
    melt = pd.melt(variable, id_vars=['ISO_Code'], var_name='Year', value_name=name)
    melt['Year'] = melt['Year'].astype('int64')
    return melt

def add_data(add):
    data1 = pd.merge(data_nckh, add, how='left', left_on=['Year', 'Country_ISO'], right_on=['Year', 'ISO_Code'])
    drop1 = data1.drop(data1.columns[-2], axis=1)
    data2 = pd.merge(drop1, add, how='left', left_on=['Year', 'Counterpart_Country_ISO'], right_on=['Year', 'ISO_Code'])
    drop2 = data2.drop(data2.columns[-2], axis=1)
    drop2.columns = drop2.columns.str.replace('_x', 'i').str.replace('_y', 'j')
    return drop2

melt_gdp = melt_data(gdp, 'GDP')
data_nckh = add_data(melt_gdp)

## Population:
melt_pop = melt_data(pop, 'P')
data_nckh = add_data(melt_pop)

## WGI i,j:
melt_cc = melt_data(cc, 'CC')
melt_ge = melt_data(ge, 'GE')
melt_pv = melt_data(pv, 'PV')
melt_rl = melt_data(rl, 'RL')
melt_rq = melt_data(rq, 'RQ')
melt_va = melt_data(va, 'VA')

data_nckh = add_data(melt_cc)
data_nckh = add_data(melt_ge)
data_nckh = add_data(melt_pv)
data_nckh = add_data(melt_rl)
data_nckh = add_data(melt_rq)
data_nckh = add_data(melt_va)


# Thêm biến tương tác giữa i và j:
## Aij, Dij:
data_nckh = pd.merge(data_nckh, dist, how='left', left_on=['Country_ISO', 'Counterpart_Country_ISO'], right_on=['Country_ISO', 'Counterpart_Country_ISO'])

## NERij:
data_nckh = pd.merge(data_nckh, exrate, how='left', left_on=['Country_Name', 'Year'], right_on=['Country', 'Year'])
data_nckh = data_nckh.drop(data_nckh.columns[-2], axis=1)
data_nckh = pd.merge(data_nckh, exrate, how='left', left_on=['Counterpart_Country_Name', 'Year'], right_on=['Country', 'Year'])
data_nckh = data_nckh.drop(data_nckh.columns[-2], axis=1)
data_nckh.columns = data_nckh.columns.str.replace('_x', 'i').str.replace('_y', 'j')


# # Xuất file bảng dữ liệu hoàn chỉnh
data_nckh.to_excel('data_nckh.xlsx')

