import pandas as pd
from sklearn.decomposition import PCA

final = pd.read_excel('./DATA FOR RESEARCH.xlsx')
wgi_i = final.loc[:, "CCi":"VAi"]
pca_i = PCA(n_components=1)
principalComponents_i = pca_i.fit_transform(wgi_i)
principalWGI_i = pd.DataFrame(data=principalComponents_i, columns=['WGIi'])

wgi_j = final.loc[:, "CCj":"VAj"]
print(wgi_j)
pca_j = PCA(n_components=1)
principalComponents_j = pca_j.fit_transform(wgi_j)
principalWGI_j = pd.DataFrame(data = principalComponents_j, columns=['WGIj'])

principalWGI = pd.merge(principalWGI_i, principalWGI_j, left_index=True, right_index=True)
superfinal = pd.merge(final, principalWGI, left_index=True, right_index=True)
superfinal.to_excel('RESEARCH DATA.xlsx')