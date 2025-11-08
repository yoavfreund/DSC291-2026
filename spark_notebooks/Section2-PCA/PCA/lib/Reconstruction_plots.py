import numpy as np
import pylab as plt
import pandas as pd

from lib.numpy_pack import packArray,unpackArray
from lib.decomposer import *
from lib.YearPlotter import YearPlotter
import matplotlib.pyplot as plt

from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets


def _row_to_dict(row):
    if isinstance(row, dict):
        return dict(row)
    if isinstance(row, pd.Series):
        return row.to_dict()
    if hasattr(row, "asDict"):
        return row.asDict()
    if hasattr(row, "_asdict"):
        return dict(row._asdict())
    raise TypeError(f"Unsupported row type: {type(row)!r}")


def _extract_values(row_dict, key="Values", value_dtype=np.float16):
    values = row_dict.get(key)
    if values is None:
        raise KeyError(f"Column '{key}' not found in row")
    if isinstance(values, (bytes, bytearray, memoryview)):
        return np.array(unpackArray(values, value_dtype), dtype=np.float64)
    return np.array(values, dtype=np.float64)


class recon_plot:
    """A class for creating an interactive demonstration of approximating 
    a function with an orthonormal set of function"""
    def __init__(self,eigen_decomp,year_axis=False,fig=None,ax=None,interactive=False,Title=None,figsize=(4,3)):
        self.eigen_decomp=eigen_decomp
        self.interactive=interactive
        self.fig=fig
        self.ax=ax
        self.Title=Title
        self.figsize=figsize
        self.i=0
        
        self.year_axis=year_axis
        self.yearPlotter=None
        if year_axis:
            self.yearPlotter=YearPlotter()
        if not self.interactive:
            self.plot_combination(**self.eigen_decomp.coeff)

    def get_Interactive(self):
        widge_list,widge_dict = self.get_widgets()
        w=interactive(self.plot_combination, **widge_dict);
        self.Title='Interactive reconstruction'
        return widgets.VBox([widgets.HBox(widge_list),w.children[-1]])

    def get_widgets(self):
        coeff=self.eigen_decomp.C
        widge_dict={}
        widge_list=[]
        for i in range(self.eigen_decomp.n):
            if coeff[i]>0:
                r=[0,coeff[i]]
            else:
                r=[coeff[i],0]

            widge_list.append(widgets.FloatSlider(min=r[0],max=r[1],step=(r[1]-r[0])/10.,
                                                  value=0,orientation='vertical',decription='v'+str(i)))
            widge_dict['c'+str(i)]=widge_list[-1]

        return widge_list,widge_dict

    def plot(self,y,label=''):
        if self.year_axis:
            self.yearPlotter.plot(y,self.fig,self.ax,label=label)
        else:
            self.ax.plot(self.eigen_decomp.x,y,label=label);

    def plot_combination(self,**coeff):
        if self.interactive or self.fig is None:
            self.fig=plt.figure(figsize=self.figsize)
            self.ax=self.fig.add_axes([0,0,1,1])

        A=self.eigen_decomp.mean
        self.plot(A,label='mean')

        for i in range(self.eigen_decomp.n):
            g=self.eigen_decomp.U[:,i]*coeff['c'+str(i)]
            A=A+g
            self.plot(A,label='c'+str(i))
        self.plot(self.eigen_decomp.f,label='target')
        self.ax.grid(figure=self.fig)        
        self.ax.legend()
        self.ax.set_title(self.Title)
        if self.interactive:
            plt.show()
        else:
            self.fig.show()
        return None


def plot_decomp(row,Mean,EigVec,fig=None,ax=None,Title=None,interactive=False,values_column="Values"):
    row_dict=_row_to_dict(row)
    target=_extract_values(row_dict, values_column)
    station=row_dict.get('station', row_dict.get('Station',''))
    year=row_dict.get('year', row_dict.get('Year',''))
    measurement=row_dict.get('measurement', row_dict.get('Measurement',''))
    if Title is None:
        Title='{} / {}    {}'.format(station, year, measurement).strip()
    x_axis=range(1, len(target)+1)
    eigen_decomp=Eigen_decomp(x_axis,target,Mean,EigVec)
    plotter=recon_plot(eigen_decomp,year_axis=True,fig=fig,ax=ax,interactive=interactive,Title=Title)
    return plotter


def plot_recon_grid(rows,Mean,EigVec,column_n=4, row_n=3, figsize=(15,10),header='c2=%3.2f,r2=%3.2f',params=('coeff_2','res_2'),values_column="Values"):
    fig,axes=plt.subplots(row_n,column_n, sharex='col', sharey='row',figsize=figsize);
    k=0
    for i in range(row_n):
        for j in range(column_n):
            row=rows[k]
            k+=1
            row_dict=_row_to_dict(row)
            P=tuple(row_dict.get(p) for p in params)
            _title=header%P if None not in P else header%tuple(0 for _ in params)
            plot_decomp(row,Mean,EigVec,fig=fig,ax=axes[i,j],Title=_title,interactive=False,values_column=values_column)
    return None