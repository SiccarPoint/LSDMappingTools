## LSDMap_ChiPlotting.py
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
## These functions are tools to deal with chi maps
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
## SMM
## 14/12/2016
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import numpy as np
import cubehelix
import matplotlib.pyplot as plt
#from cycler import cycler
from matplotlib import rcParams
import LSDMap_GDALIO as LSDMap_IO
#import LSDMap_BasicManipulation as LSDMap_BM
#import LSDMap_OSystemTools as LSDOst
import LSDMap_BasicPlotting as LSDMap_BP
import LSDMap_PointData as LSDMap_PD

##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
## This function plots the chi slope on a shaded relief map
## It uses the Kirby and Whipple colour scheme
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def BasicChiPlotGridPlotKirby(FileName, DrapeName, chi_csv_fname, thiscmap='gray',drape_cmap='gray',
                            colorbarlabel='Elevation in meters',clim_val = (0,0),
                            drape_alpha = 0.6,FigFileName = 'Image.pdf',FigFormat = 'show',
                            elevation_threshold = 0, size_format = "ESURF"):

    """This function plots the chi slope on a shaded relief map. It uses the Kirby and Whipple colour scheme.

    Args:
        FileName (str): The name (with full path and extension) of the DEM.
        DrapenName (str): The name (with full path and extension) of the drape file (usually a hillshade, but could be anything)
        chi_csv_fname (str): The name (with full path and extension) of the cdv file with chi, chi slope, etc information. This file is produced by the chi_mapping_tool. 
        thiscmap (colormap): The colourmap for the elevation raster
        drape_cmap (colormap):  The colourmap for the drape raster
        colorbarlabel (str): the text label on the colourbar. 
        clim_val  (float,float): The colour limits for the drape file. If (0,0) it uses the minimum and maximum values of the drape file. Users can assign numbers to get consistent colourmaps between plots. 
        drape_alpha (float): The alpha value of the drape
        FigFileName (str): The name of the figure file
        FigFormat (str): The format of the figure. Usually 'png' or 'pdf'. If "show" then it calls the matplotlib show() command. 
        elevation_threshold (float): elevation_threshold chi points below this elevation are removed from plotting. 
        size_format (str): Can be "big" (16 inches wide), "geomorphology" (6.25 inches wide), or "ESURF" (4.92 inches wide) (defualt esurf). 
 
    Returns:
        Does not return anything but makes a plot.
        
    Author: SMM
    """
    
    from matplotlib import colors

    label_size = 10

    # Set up fonts for plots
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = label_size 
    #plt.rc('text', usetex=True)

    # get the data
    raster = LSDMap_IO.ReadRasterArrayBlocks(FileName)
    raster_drape = LSDMap_IO.ReadRasterArrayBlocks(DrapeName)

    # now get the extent
    extent_raster = LSDMap_IO.GetRasterExtent(FileName)
    
    x_min = extent_raster[0]
    x_max = extent_raster[1]
    y_min = extent_raster[2]
    y_max = extent_raster[3]

    # make a figure, 
    if size_format == "geomorphology":
        fig = plt.figure(1, facecolor='white',figsize=(6.25,5))
        l_pad = -40
    elif size_format == "big":
        fig = plt.figure(1, facecolor='white',figsize=(16,9))
        l_pad = -50
    else:
        fig = plt.figure(1, facecolor='white',figsize=(4.92126,3.5))
        l_pad = -35

    gs = plt.GridSpec(100,100,bottom=0.25,left=0.1,right=1.0,top=1.0)
    ax = fig.add_subplot(gs[25:100,10:95])

    gs = plt.GridSpec(100,100,bottom=0.25,left=0.1,right=1.0,top=1.0)
    ax = fig.add_subplot(gs[25:100,10:95])
    
    # This is the axis for the colorbar
    ax2 = fig.add_subplot(gs[10:15,15:70])

    # now get the tick marks    
    n_target_tics = 5
    xlocs,ylocs,new_x_labels,new_y_labels = LSDMap_BP.GetTicksForUTM(FileName,x_max,x_min,y_max,y_min,n_target_tics)  

    im1 = ax.imshow(raster[::-1], thiscmap, extent = extent_raster, interpolation="nearest")
    
    # set the colour limits
    print "Setting colour limits to "+str(clim_val[0])+" and "+str(clim_val[1])
    if (clim_val == (0,0)):
        print "Im setting colour limits based on minimum and maximum values"
        im1.set_clim(0, np.nanmax(raster))
    else:
        print "Now setting colour limits to "+str(clim_val[0])+" and "+str(clim_val[1])
        im1.set_clim(clim_val[0],clim_val[1])
   
    plt.hold(True)
   
    # Now for the drape: it is in grayscale
    #print "drape_cmap is: "+drape_cmap
    im3 = ax.imshow(raster_drape[::-1], drape_cmap, extent = extent_raster, alpha = drape_alpha, interpolation="nearest")

    # Set the colour limits of the drape
    im3.set_clim(0,np.nanmax(raster_drape))

    ax.spines['top'].set_linewidth(1)
    ax.spines['left'].set_linewidth(1)
    ax.spines['right'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1) 
 
    ax.set_xticklabels(new_x_labels,rotation=60)
    ax.set_yticklabels(new_y_labels)  
    
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")  

    # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
    ax.tick_params(axis='both', width=1, pad = 2)
    for tick in ax.xaxis.get_major_ticks():
        tick.set_pad(2)    

    # Now we get the chi points
    EPSG_string = LSDMap_IO.GetUTMEPSG(FileName)
    print "EPSG string is: " + EPSG_string
    
    thisPointData = LSDMap_PD.LSDMap_PointData(chi_csv_fname) 
    thisPointData.ThinData('elevation',elevation_threshold)
    
    # convert to easting and northing
    [easting,northing] = thisPointData.GetUTMEastingNorthing(EPSG_string)
    
    
    # The image is inverted so we have to invert the northing coordinate
    Ncoord = np.asarray(northing)
    Ncoord = np.subtract(extent_raster[3],Ncoord)
    Ncoord = np.add(Ncoord,extent_raster[2])
    
    M_chi = thisPointData.QueryData('m_chi')
    #print M_chi
    M_chi = [float(x) for x in M_chi]
    
    
    # make a color map of fixed colors
    this_cmap = colors.ListedColormap(['#2c7bb6','#abd9e9','#ffffbf','#fdae61','#d7191c'])
    bounds=[0,50,100,175,250,1205]
    norm = colors.BoundaryNorm(bounds, this_cmap.N)
    
    sc = ax.scatter(easting,Ncoord,s=0.5, c=M_chi,cmap=this_cmap,norm=norm,edgecolors='none')

    # This affects all axes because we set share_all = True.
    ax.set_xlim(x_min,x_max)    
    ax.set_ylim(y_max,y_min)     

    ax.set_xticks(xlocs)
    ax.set_yticks(ylocs)   
    
    cbar = plt.colorbar(sc,cmap=this_cmap,norm=norm,spacing='uniform', ticks=bounds, boundaries=bounds,orientation='horizontal',cax=ax2)
    cbar.set_label(colorbarlabel, fontsize=10)
    ax2.set_xlabel(colorbarlabel, fontname='Arial',labelpad=l_pad)    

    print "The figure format is: " + FigFormat
    if FigFormat == 'show':    
        plt.show()
    elif FigFormat == 'return':
        return fig 
    else:
        plt.savefig(FigFileName,format=FigFormat,dpi=500)
        fig.clf()


##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def FindSourceInformation(thisPointData):    
    """This function finds the source locations, with chi elevation, flow distance, etc.

    Args:
        thisPointData (LSDMap_PointData) A LSDMap_PointData object that is derived from the Chi_mapping_tool component of *LSDTopoTools*.

    Returns:
        A dict with key of the source node that returns a dict that has the FlowDistance, Chi, and Elevation of each source.
        Used for plotting source numbers on profile plots. 
        
    Author: SMM 
    """    
    
    # Get the chi, m_chi, basin number, and source ID code
    chi = thisPointData.QueryData('chi')
    chi = [float(x) for x in chi]
    elevation = thisPointData.QueryData('elevation')
    elevation = [float(x) for x in elevation]
    fdist = thisPointData.QueryData('flow distance')
    fdist = [float(x) for x in fdist]        
    source = thisPointData.QueryData('source_key')
    source = [int(x) for x in source]
    latitude = thisPointData.GetLatitude()
    longitude = thisPointData.GetLongitude()
   
  
    
    
    Chi = np.asarray(chi)
    Elevation = np.asarray(elevation)
    Fdist = np.asarray(fdist)
    Source = np.asarray(source)
    Latitude = np.asarray(latitude)
    Longitude = np.asarray(longitude)

    n_sources = Source.max()+1
    print("N sources is: "+str(n_sources))
 
    # This loops through all the source indices, and then picks out the
    # Elevation, chi coordinate and flow distance of each node
    # Then it returns a dictionary containing the elements of the node
    these_source_nodes = {}
    for src_idx in range(0,n_sources-1):
        m = np.ma.masked_where(Source!=src_idx, Source)
        
        # Mask the unwanted values
        maskX = np.ma.masked_where(np.ma.getmask(m), Chi)
        maskElevation = np.ma.masked_where(np.ma.getmask(m), Elevation)
        maskFlowDistance = np.ma.masked_where(np.ma.getmask(m), Fdist)
        maskLatitude = np.ma.masked_where(np.ma.getmask(m), Latitude)
        maskLongitude= np.ma.masked_where(np.ma.getmask(m), Longitude)
        
        # get the locations of the source         
        this_dict = {}
        idx_of_max_FD = maskX.argmax()
        this_dict["FlowDistance"]=maskFlowDistance[idx_of_max_FD]
        this_dict["Chi"]=maskX[idx_of_max_FD]
        this_dict["Elevation"]=maskElevation[idx_of_max_FD]
        this_dict["Latitude"]=maskLatitude[idx_of_max_FD]
        this_dict["Longitude"]=maskLongitude[idx_of_max_FD]
        
        # get the minimum of the source
        idx_of_min_Chi = maskX.argmin()
        chi_length = maskX[idx_of_max_FD]-maskX[idx_of_min_Chi]
        this_dict["SourceLength"]=chi_length

        these_source_nodes[src_idx] = this_dict
        
    return these_source_nodes

##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=        
def FindShortSourceChannels(these_source_nodes,threshold_length):         
    """This function gets the list of sources that are shorter than a threshold value
    
    Args: 
        these_source_nodes (dict): A dict from the FindSourceInformation module
        threshold_length (float): The threshold of chi lenght of the source segment
    
    Return:
        long_sources: A list of integers of source with the appropriate length
    
    Author: SMM
    """
    long_sources = []
    for key in these_source_nodes:
        if these_source_nodes[key]["SourceLength"] > threshold_length:
            long_sources.append(key)
    
    return long_sources        
    

##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
## This function plots the chi slope on a shaded relief map
## It uses a cubehelix colourmap over the log 10 of the channel steepness
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def BasicChiPlotGridPlot(FileName, DrapeName, chi_csv_fname, thiscmap='gray',drape_cmap='gray',
                            colorbarlabel='log$_{10}k_{sn}$',clim_val = (0,0),
                            drape_alpha = 0.6,FigFileName = 'Image.pdf',FigFormat = 'show',
                            elevation_threshold = 0, size_format = "ESURF"):

    """This is the main chi plotting script that prints a chi steepness map over the hillshade. Note that the colour scale for the chi slope values are always cubehelix

    Args:
        FileName (str): The name (with full path and extension) of the DEM.
        DrapenName (str): The name (with full path and extension) of the drape file (usually a hillshade, but could be anything)
        chi_csv_fname (str): The name (with full path and extension) of the cdv file with chi, chi slope, etc information. This file is produced by the chi_mapping_tool. 
        thiscmap (colormap): The colourmap for the elevation raster
        drape_cmap (colormap):  The colourmap for the drape raster
        colorbarlabel (str): the text label on the colourbar. 
        clim_val  (float,float): The colour limits for the drape file. If (0,0) it uses the minimum and maximum values of the drape file. Users can assign numbers to get consistent colourmaps between plots. 
        drape_alpha (float): The alpha value of the drape
        FigFileName (str): The name of the figure file
        FigFormat (str): The format of the figure. Usually 'png' or 'pdf'. If "show" then it calls the matplotlib show() command. 
        elevation_threshold (float): elevation_threshold chi points below this elevation are removed from plotting.
        size_format (str): Can be "big" (16 inches wide), "geomorphology" (6.25 inches wide), or "ESURF" (4.92 inches wide) (defualt esurf). 
       
    Returns:
        Prints a plot to file.
        
    Author: 
        Simon M. Mudd

    """       
    
    import math
    label_size = 10

    # Set up fonts for plots
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = label_size 

    # get the data
    raster = LSDMap_IO.ReadRasterArrayBlocks(FileName)
    raster_drape = LSDMap_IO.ReadRasterArrayBlocks(DrapeName)

    # now get the extent
    extent_raster = LSDMap_IO.GetRasterExtent(FileName)
    x_min = extent_raster[0]
    x_max = extent_raster[1]
    y_min = extent_raster[2]
    y_max = extent_raster[3]
    
    # make a figure, 
    if size_format == "geomorphology":
        fig = plt.figure(1, facecolor='white',figsize=(6.25,5))
        l_pad = -40
    elif size_format == "big":
        fig = plt.figure(1, facecolor='white',figsize=(16,9))
        l_pad = -50
    else:
        fig = plt.figure(1, facecolor='white',figsize=(4.92126,3.5))
        l_pad = -35
        
    gs = plt.GridSpec(100,100,bottom=0.25,left=0.1,right=1.0,top=1.0)
    ax = fig.add_subplot(gs[25:100,10:95])

    # now get the tick marks    
    n_target_tics = 5
    xlocs,ylocs,new_x_labels,new_y_labels = LSDMap_BP.GetTicksForUTM(FileName,x_max,x_min,y_max,y_min,n_target_tics)  

    im1 = ax.imshow(raster[::-1], thiscmap, extent = extent_raster, interpolation="nearest")
    
    # set the colour limits
    print "Setting colour limits to "+str(clim_val[0])+" and "+str(clim_val[1])
    if (clim_val == (0,0)):
        print "Im setting colour limits based on minimum and maximum values"
        im1.set_clim(0, np.nanmax(raster))
    else:
        print "Now setting colour limits to "+str(clim_val[0])+" and "+str(clim_val[1])
        im1.set_clim(clim_val[0],clim_val[1])
   
    plt.hold(True)
   
    # Now for the drape: it is in grayscale
    #print "drape_cmap is: "+drape_cmap
    im3 = ax.imshow(raster_drape[::-1], drape_cmap, extent = extent_raster, alpha = drape_alpha, interpolation="nearest")

    # Set the colour limits of the drape
    im3.set_clim(0,np.nanmax(raster_drape))

    # Set up axes and ticks   
    ax.spines['top'].set_linewidth(1)
    ax.spines['left'].set_linewidth(1)
    ax.spines['right'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1) 
    ax.set_xticklabels(new_x_labels,rotation=60)
    ax.set_yticklabels(new_y_labels)  
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")  

    # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
    ax.tick_params(axis='both', width=1, pad = 2)
    for tick in ax.xaxis.get_major_ticks():
        tick.set_pad(2)    

    # Now we get the chi points
    EPSG_string = LSDMap_IO.GetUTMEPSG(FileName)
    print "EPSG string is: " + EPSG_string
    
    thisPointData = LSDMap_PD.LSDMap_PointData(chi_csv_fname) 
    thisPointData.ThinData('elevation',elevation_threshold)
    
    # convert to easting and northing
    [easting,northing] = thisPointData.GetUTMEastingNorthing(EPSG_string)
       
    # The image is inverted so we have to invert the northing coordinate
    Ncoord = np.asarray(northing)
    Ncoord = np.subtract(extent_raster[3],Ncoord)
    Ncoord = np.add(Ncoord,extent_raster[2])
    
    M_chi = thisPointData.QueryData('m_chi')
    M_chi = [float(x) for x in M_chi]


    log_m_chi = []
    for value in M_chi:
        if value < 0.1:
            log_m_chi.append(0)
        else:
            log_m_chi.append(math.log10(value))
    colorbarlabel = "log$_{10}k_{sn}$"    

    this_cmap = cubehelix.cmap(rot=1, reverse=True,start=3,gamma=1.0,sat=2.0)
    sc = ax.scatter(easting,Ncoord,s=0.5, c=log_m_chi,cmap=this_cmap,edgecolors='none')
    
    # set the colour limits
    sc.set_clim(0, np.nanmax(log_m_chi))


    # This is the axis for the colorbar   
    ax2 = fig.add_subplot(gs[10:15,15:70])
    plt.colorbar(sc,cmap=this_cmap,spacing='uniform', orientation='horizontal',cax=ax2)   
    ax2.set_xlabel(colorbarlabel, fontname='Arial',labelpad=l_pad)       
    
    # This affects all axes because we set share_all = True.
    ax.set_xlim(x_min,x_max)    
    ax.set_ylim(y_max,y_min)     

    ax.set_xticks(xlocs)
    ax.set_yticks(ylocs)   

    print "The figure format is: " + FigFormat
    if FigFormat == 'show':    
        plt.show()
    elif FigFormat == 'return':
        return fig 
    else:
        plt.savefig(FigFileName,format=FigFormat,dpi=750)
        fig.clf()


        
        
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
## This function plots channels, color coded
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def BasicChannelPlotGridPlotCategories(FileName, DrapeName, chi_csv_fname, thiscmap='gray',drape_cmap='gray',
                            colorbarlabel='Elevation in meters',clim_val = (0,0),
                            drape_alpha = 0.6,FigFileName = 'Image.pdf',FigFormat = 'show',
                            elevation_threshold = 0, data_name = 'source_key',
                            size_format = "ESURF"):
    """This plots the channels over a draped plot, colour coded by source

    Args:
        FileName (str): The name (with full path and extension) of the DEM.
        DrapenName (str): The name (with full path and extension) of the drape file (usually a hillshade, but could be anything)
        chi_csv_fname (str): The name (with full path and extension) of the cdv file with chi, chi slope, etc information. This file is produced by the chi_mapping_tool. 
        thiscmap (colormap): The colourmap for the elevation raster
        drape_cmap (colormap):  The colourmap for the drape raster
        colorbarlabel (str): the text label on the colourbar. 
        clim_val  (float,float): The colour limits for the drape file. If (0,0) it uses the minimum and maximum values of the drape file. Users can assign numbers to get consistent colourmaps between plots. 
        drape_alpha (float): The alpha value of the drape
        FigFileName (str): The name of the figure file
        FigFormat (str): The format of the figure. Usually 'png' or 'pdf'. If "show" then it calls the matplotlib show() command. 
        elevation_threshold (float): elevation_threshold chi points below this elevation are removed from plotting.
        data_name (str) = The name of the sources csv
        size_format (str): Can be "big" (16 inches wide), "geomorphology" (6.25 inches wide), or "ESURF" (4.92 inches wide) (defualt esurf). 
        
    Returns:
        Prints a plot to file.
        
    Author: 
        Simon M. Mudd

    """           
    from matplotlib import colors
    label_size = 10

    # Set up fonts for plots
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = label_size 
    #plt.rc('text', usetex=True)

    # get the data
    raster = LSDMap_IO.ReadRasterArrayBlocks(FileName)
    raster_drape = LSDMap_IO.ReadRasterArrayBlocks(DrapeName)
   
    # now get the extent
    extent_raster = LSDMap_IO.GetRasterExtent(FileName)
    
    x_min = extent_raster[0]
    x_max = extent_raster[1]
    y_min = extent_raster[2]
    y_max = extent_raster[3]

    # make a figure, 
    if size_format == "geomorphology":
        fig = plt.figure(1, facecolor='white',figsize=(6.25,5))
    elif size_format == "big":
        fig = plt.figure(1, facecolor='white',figsize=(16,9))
    else:
        fig = plt.figure(1, facecolor='white',figsize=(4.92126,3.5))
        
    gs = plt.GridSpec(100,100,bottom=0.25,left=0.1,right=1.0,top=1.0)
    ax = fig.add_subplot(gs[25:100,10:95])

    # now get the tick marks    
    n_target_tics = 5
    xlocs,ylocs,new_x_labels,new_y_labels = LSDMap_BP.GetTicksForUTM(FileName,x_max,x_min,y_max,y_min,n_target_tics)  

    im1 = ax.imshow(raster[::-1], thiscmap, extent = extent_raster, interpolation="nearest")  

    # set the colour limits
    print "Setting colour limits to "+str(clim_val[0])+" and "+str(clim_val[1])
    if (clim_val == (0,0)):
        print "Im setting colour limits based on minimum and maximum values"
        im1.set_clim(0, np.nanmax(raster))
    else:
        print "Now setting colour limits to "+str(clim_val[0])+" and "+str(clim_val[1])
        im1.set_clim(clim_val[0],clim_val[1])
   
    plt.hold(True)
   
    # Now for the drape: it is in grayscale
    #print "drape_cmap is: "+drape_cmap
    im3 = ax.imshow(raster_drape[::-1], drape_cmap, extent = extent_raster, alpha = drape_alpha, interpolation="nearest")

    # Set the colour limits of the drape
    im3.set_clim(0,np.nanmax(raster_drape))
    
    
    ax.spines['top'].set_linewidth(1)
    ax.spines['left'].set_linewidth(1)
    ax.spines['right'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1) 
    
    ax.set_xticklabels(new_x_labels,rotation=60)
    ax.set_yticklabels(new_y_labels)  
    
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")  

    # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
    ax.tick_params(axis='both', width=1, pad = 2)
    for tick in ax.xaxis.get_major_ticks():
        tick.set_pad(2)    

    # Now we get the chi points
    EPSG_string = LSDMap_IO.GetUTMEPSG(FileName)
    print "EPSG string is: " + EPSG_string
    
    thisPointData = LSDMap_PD.LSDMap_PointData(chi_csv_fname) 
    thisPointData.ThinData('elevation',elevation_threshold)
    
    # convert to easting and northing
    [easting,northing] = thisPointData.GetUTMEastingNorthing(EPSG_string)
 
    # The image is inverted so we have to invert the northing coordinate
    Ncoord = np.asarray(northing)
    Ncoord = np.subtract(extent_raster[3],Ncoord)
    Ncoord = np.add(Ncoord,extent_raster[2])
    
    these_data = thisPointData.QueryData(data_name)
    #print M_chi
    these_data = [int(x) for x in these_data]

    # make a color map of fixed colors
    NUM_COLORS = 15

    this_cmap = plt.cm.Set1
    cNorm  = colors.Normalize(vmin=0, vmax=NUM_COLORS-1)
    plt.cm.ScalarMappable(norm=cNorm, cmap=this_cmap)
    channel_data = [x % NUM_COLORS for x in these_data]

    ax.scatter(easting,Ncoord,s=0.5, c=channel_data,norm=cNorm,cmap=this_cmap,edgecolors='none')

    # This affects all axes because we set share_all = True.
    ax.set_xlim(x_min,x_max)    
    ax.set_ylim(y_max,y_min)     

    ax.set_xticks(xlocs)
    ax.set_yticks(ylocs)   
    ax.set_title('Channels colored by source number')

    print "The figure format is: " + FigFormat
    if FigFormat == 'show':    
        plt.show()
    elif FigFormat == 'return':
        return fig 
    else:
        plt.savefig(FigFileName,format=FigFormat,dpi=500)
        fig.clf() 
        
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
## This function plots channels, color coded
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=        
def ChiProfiles(chi_csv_fname, FigFileName = 'Image.pdf',FigFormat = 'show',
                basin_order_list = [],basin_rename_list = [],
                label_sources = False,
                elevation_threshold = 0,
                source_thinning_threshold = 0,
                size_format = "ESURF"):
    """This function plots the chi vs elevation: lumps everything onto the same axis. This tends to make a mess. 
 
    Args:
        chi_csv_fname (str): The name (with full path and extension) of the cdv file with chi, chi slope, etc information. This file is produced by the chi_mapping_tool. 
        FigFileName (str): The name of the figure file
        FigFormat (str): The format of the figure. Usually 'png' or 'pdf'. If "show" then it calls the matplotlib show() command. 
        basin_order_list (int list): The basins to plot
        basin_rename_list (int list): A list for naming substitutions
        label_sources (bool): If tru, label the sources.
        elevation_threshold (float): elevation_threshold chi points below this elevation are removed from plotting.
        source_thinning_threshold (float) = Minimum chi lenght of a source segment
        size_format (str): Can be "big" (16 inches wide), "geomorphology" (6.25 inches wide), or "ESURF" (4.92 inches wide) (defualt esurf). 
 
    Returns:
         Does not return anything but makes a plot.
         
    Author: SMM
    """

    from matplotlib import colors
    from adjust_text import adjust_text
    
    label_size = 10

    # Set up fonts for plots
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = label_size     
   
    # make a figure, 
    if size_format == "geomorphology":
        fig = plt.figure(1, facecolor='white',figsize=(6.25,5))
    elif size_format == "big":
        fig = plt.figure(1, facecolor='white',figsize=(16,9))
    else:
        fig = plt.figure(1, facecolor='white',figsize=(4.92126,3.5))
        
    gs = plt.GridSpec(100,100,bottom=0.25,left=0.1,right=1.0,top=1.0)
    ax = fig.add_subplot(gs[25:100,10:95])
 
    thisPointData = LSDMap_PD.LSDMap_PointData(chi_csv_fname) 
    thisPointData.ThinData('elevation',elevation_threshold)

    
    # Logic for thinning the sources    
    if source_thinning_threshold > 0:
        print("I am going to thin some sources out for you")
        source_info = FindSourceInformation(thisPointData)
        remaining_sources = FindShortSourceChannels(source_info,source_thinning_threshold)
        thisPointData.ThinDataSelection("source_key",remaining_sources)
               
    # Logic for stacked labels. You need to run this after source thinning to 
    # get an updated source dict
    if label_sources:
        source_info = FindSourceInformation(thisPointData)

    
    # Get the chi, m_chi, basin number, and source ID code
    chi = thisPointData.QueryData('chi')
    chi = [float(x) for x in chi]
    elevation = thisPointData.QueryData('elevation')
    elevation = [float(x) for x in elevation]
    fdist = thisPointData.QueryData('flow distance')
    fdist = [float(x) for x in fdist]     
    m_chi = thisPointData.QueryData('m_chi')
    m_chi = [float(x) for x in m_chi]    
    basin = thisPointData.QueryData('basin_key')
    basin = [int(x) for x in basin] 
    source = thisPointData.QueryData('source_key')
    source = [int(x) for x in source]

    # need to convert everything into arrays so we can mask different basins
    Chi = np.asarray(chi)
    Elevation = np.asarray(elevation)
    #Fdist = np.asarray(fdist)
    #M_chi = np.asarray(m_chi)
    Basin = np.asarray(basin)
    Source = np.asarray(source)
    
    #max_basin = np.amax(Basin)
    max_chi = np.amax(Chi)
    max_Elevation = np.amax(Elevation)
    #max_M_chi = np.amax(M_chi)
    min_Elevation = np.amin(Elevation)
    
    z_axis_min = int(min_Elevation/10)*10 
    z_axis_max = int(max_Elevation/10)*10+10
    chi_axis_max = int(max_chi/5)*5+5
    
    # make a color map of fixed colors
    NUM_COLORS = 15

    this_cmap = plt.cm.Set1
    cNorm  = colors.Normalize(vmin=0, vmax=NUM_COLORS-1)    
    Basin_colors = [x % NUM_COLORS for x in Basin]

    
    dot_pos = FigFileName.rindex('.')
    newFilename = FigFileName[:dot_pos]+FigFileName[dot_pos:]
    print "newFilename: "+newFilename

    texts = []
    bbox_props = dict(boxstyle="circle,pad=0.1", fc="w", ec="k", lw=0.5,alpha = 0.25)
    for basin_number in basin_order_list:
        
        print ("This basin is: " +str(basin_number))

        m = np.ma.masked_where(Basin!=basin_number, Basin)
        maskX = np.ma.masked_where(np.ma.getmask(m), Chi)
        maskElevation = np.ma.masked_where(np.ma.getmask(m), Elevation)
        maskBasin = np.ma.masked_where(np.ma.getmask(m), Basin_colors)
        maskSource = np.ma.masked_where(np.ma.getmask(m), Source)
    
        # logic for source labeling
        if label_sources:
                      
            # Convert the masked data to a list and then that list to a set and
            # back to a list (phew!)            
            list_source = maskSource.tolist()
            set_source = set(list_source)
            list_source = list(set_source)
            
            # Now we have to get rid of stupid non values
            list_source = [x for x in list_source if x is not None]

            print("these sources are: ")
            print list_source            
            
            for this_source in list_source:
                source_Chi= source_info[this_source]["Chi"]
                source_Elevation = source_info[this_source]["Elevation"]
                #print("Source is: "+str(this_source))
                #print("Chi is: "+str(source_info[this_source]["Chi"]))
                #print("FlowDistance is is: "+str(source_info[this_source]["FlowDistance"]))
                #print("Elevation is: "+str(source_info[this_source]["Elevation"]))
                texts.append(ax.text(source_Chi, source_Elevation, str(this_source), style='italic',
                        verticalalignment='bottom', horizontalalignment='left',fontsize=8,bbox=bbox_props))
                
        
        ax.scatter(maskX,maskElevation,s=2.0, c=maskBasin,norm=cNorm,cmap=this_cmap,edgecolors='none')
    

    
    ax.spines['top'].set_linewidth(1)
    ax.spines['left'].set_linewidth(1)
    ax.spines['right'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1) 

    ax.set_xlabel("$\chi$")
    ax.set_ylabel("Elevation (m)") 
    
    # This affects all axes because we set share_all = True.
    ax.set_ylim(z_axis_min,z_axis_max)    
    ax.set_xlim(0,chi_axis_max)      

        
    #print("Number of text elements is: "+str(len(texts)))    
    adjust_text(texts)
    #print("Now the number of text elements is: "+str(len(texts)))      
    
    
    # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
    ax.tick_params(axis='both', width=1, pad = 2)
    for tick in ax.xaxis.get_major_ticks():
        tick.set_pad(2)       

    print "The figure format is: " + FigFormat
    if FigFormat == 'show':    
        plt.show()
    elif FigFormat == 'return':
        return fig 
    else:
        plt.savefig(newFilename,format=FigFormat,dpi=500)
        fig.clf()     
        
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
## This function plots channels, color coded
## Only plot the source colouring, not the chi gradient!!
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=        
def StackedChiProfiles(chi_csv_fname, FigFileName = 'Image.pdf',
                       FigFormat = 'show',elevation_threshold = 0, 
                       first_basin = 0, last_basin = 0,
                       basin_order_list = [],basin_rename_list = [],
                       X_offset = 5,label_sources = False,
                       size_format = "ESURF"):
    """This function plots the chi vs elevation: It stacks profiles (so the basins are spaced out) and colours them by the source number.
 
    Args:
        chi_csv_fname (str): The name (with full path and extension) of the cdv file with chi, chi slope, etc information. This file is produced by the chi_mapping_tool. 
        FigFileName (str): The name of the figure file
        FigFormat (str): The format of the figure. Usually 'png' or 'pdf'. If "show" then it calls the matplotlib show() command. 
        elevation_threshold (float): elevation_threshold chi points below this elevation are removed from plotting.
        first_basin (int): The basin to start with (but overridden by the basin list)
        last_basin (int): The basin to end with (but overridden by the basin list)       
        basin_order_list (int list): The basins to plot
        basin_rename_list (int list): A list for naming substitutions. Useful because LSDTopoTools might number basins in a way a human wouldn't, so a user can intervene in the names. 
        X_offset (float): The offest in chi between the basins along the x-axis. Used to space out the profiles so you can see each of them.        
        label_sources (bool): If true, label the sources.
        source_thinning_threshold (float) = Minimum chi lenght of a source segment
        size_format (str): Can be "big" (16 inches wide), "geomorphology" (6.25 inches wide), or "ESURF" (4.92 inches wide) (defualt esurf). 
 
    Returns:
         Does not return anything but makes a plot.
         
    Author: SMM
    """

    from adjust_text import adjust_text
    from matplotlib import colors
    import matplotlib.patches as patches

    label_size = 10

    # Set up fonts for plots
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = label_size     
   

    # make a figure 
    if size_format == "geomorphology":
        fig = plt.figure(1, facecolor='white',figsize=(6.25,5))
    elif size_format == "big":
        fig = plt.figure(1, facecolor='white',figsize=(16,9))
    else:
        fig = plt.figure(1, facecolor='white',figsize=(4.92126,3.5))

    gs = plt.GridSpec(100,100,bottom=0.25,left=0.1,right=1.0,top=1.0)
    ax = fig.add_subplot(gs[25:100,10:95])

    thisPointData = LSDMap_PD.LSDMap_PointData(chi_csv_fname) 
    thisPointData.ThinData('elevation',elevation_threshold)
    
    # Get the chi, m_chi, basin number, and source ID code
    chi = thisPointData.QueryData('chi')
    chi = [float(x) for x in chi]
    elevation = thisPointData.QueryData('elevation')
    elevation = [float(x) for x in elevation]
    fdist = thisPointData.QueryData('flow distance')
    fdist = [float(x) for x in fdist]     
    m_chi = thisPointData.QueryData('m_chi')
    m_chi = [float(x) for x in m_chi]    
    basin = thisPointData.QueryData('basin_key')
    basin = [int(x) for x in basin] 
    source = thisPointData.QueryData('source_key')
    source = [int(x) for x in source]

    # need to convert everything into arrays so we can mask different basins
    Chi = np.asarray(chi)
    Elevation = np.asarray(elevation)
    #Fdist = np.asarray(fdist)
    #M_chi = np.asarray(m_chi)
    Basin = np.asarray(basin)
    Source = np.asarray(source)
    
    max_basin = np.amax(Basin)
    max_chi = np.amax(Chi)
    max_Elevation = np.amax(Elevation)
    #max_M_chi = np.amax(M_chi)
    min_Elevation = np.amin(Elevation)

    # determine the maximum and minimum elevations    
    z_axis_min = int(min_Elevation/10)*10 
    z_axis_max = int(max_Elevation/10)*10+10
    X_axis_max = int(max_chi/5)*5+5
    
    elevation_range = z_axis_max-z_axis_min
    z_axis_min = z_axis_min - 0.075*elevation_range 


    # Logic for stacked labels
    if label_sources:
        source_info = FindSourceInformation(thisPointData)


    # Now calculate the spacing of the stacks
    this_X_offset = 0
    if basin_order_list:
        basins_list = basin_order_list
        
        n_stacks = len(basins_list)
        added_X = X_offset*n_stacks
        X_axis_max = X_axis_max+added_X        
    else:
        # now loop through a number of basins
        if last_basin >= max_basin:
            last_basin = max_basin-1
    
        if first_basin > last_basin:
            first_basin = last_basin
            print("Your first basin was larger than last basin. I won't plot anything")
        basins_list = list(range(first_basin,last_basin+1))
 
        n_stacks = last_basin-first_basin+1
        added_X = X_offset*n_stacks
        print("The number of stacks is: "+str(n_stacks)+" the old max: "+str(X_axis_max))    
        X_axis_max = X_axis_max+added_X
        print("The nex max is: "+str(X_axis_max))
 
   
    # make a color map of fixed colors
    NUM_COLORS = 15

    this_cmap = plt.cm.Set1
    cNorm  = colors.Normalize(vmin=0, vmax=NUM_COLORS-1)
    #scalarMap = plt.cm.ScalarMappable(norm=cNorm, cmap=this_cmap)      
    Source_colors = [x % NUM_COLORS for x in Source]
    plt.hold(True) 
   
    dot_pos = FigFileName.rindex('.')
    newFilename = FigFileName[:dot_pos]+'_Stack'+str(first_basin)+FigFileName[dot_pos:]
    
    texts = []  
    for basin_number in basins_list:
        
        print ("This basin is: " +str(basin_number))

        m = np.ma.masked_where(Basin!=basin_number, Basin)
        maskX = np.ma.masked_where(np.ma.getmask(m), Chi)
        maskElevation = np.ma.masked_where(np.ma.getmask(m), Elevation)
        maskSource = np.ma.masked_where(np.ma.getmask(m), Source_colors)

        print("adding an offset of: "+str(this_X_offset))
        
        maskX = np.add(maskX,this_X_offset)
        
        this_min_x = np.nanmin(maskX)
        this_max_x =np.nanmax(maskX)
        width_box = this_max_x-this_min_x
        
        print("Min: "+str(this_min_x)+" Max: "+str(this_max_x))
        ax.add_patch(patches.Rectangle((this_min_x,z_axis_min), width_box, z_axis_max-z_axis_min,alpha = 0.01,facecolor='r',zorder=-10))      
        
        if basin_number == basins_list[-1]:
            print("last basin, geting maximum value,basin is: "+str(basin_number))
            this_max = np.amax(maskX)
            this_max = int(this_max/5)*5+5
            print("The rounded maximum is: "+str(this_max))
            chi_axis_max = this_max
        
        #Source_colors = [x % NUM_COLORS for x in maskSource]

        # some logic for the basin rename
        if basin_rename_list:
            if len(basin_rename_list) == max_basin+1:
                this_basin_text = "Basin "+str(basin_rename_list[basin_number])
        else:
            this_basin_text = "Basin "+str(basin_number)      
        
          
        ax.text(this_min_x+0.1*width_box, z_axis_min+0.025*elevation_range, this_basin_text, style='italic',
                verticalalignment='bottom', horizontalalignment='left',fontsize=8)

        # logic for source labeling
        if label_sources:
                      
            # Convert the masked data to a list and then that list to a set and
            # back to a list (phew!)            
            list_source = maskSource.tolist()
            set_source = set(list_source)
            list_source = list(set_source)
            
            # Now we have to get rid of stupid non values
            list_source = [x for x in list_source if x is not None]

            print("these sources are: ")
            print list_source            
            
            for this_source in list_source:
                source_Chi= source_info[this_source]["Chi"]
                source_Elevation = source_info[this_source]["Elevation"]
                print("Source is: "+str(this_source))
                #print("Chi is: "+str(source_info[this_source]["Chi"]))
                #print("FlowDistance is is: "+str(source_info[this_source]["FlowDistance"]))
                #print("Elevation is: "+str(source_info[this_source]["Elevation"]))
                texts.append(ax.text(source_Chi+this_X_offset, source_Elevation, str(this_source), style='italic',
                        verticalalignment='bottom', horizontalalignment='left',fontsize=8))
                
        
        ax.scatter(maskX,maskElevation,s=2.0, c=maskSource,norm=cNorm,cmap=this_cmap,edgecolors='none')
        this_X_offset = this_X_offset+X_offset
     
    
    ax.spines['top'].set_linewidth(1)
    ax.spines['left'].set_linewidth(1)
    ax.spines['right'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1) 

    ax.set_xlabel("$\chi$ (m)")
    ax.set_ylabel("Elevation (m)") 
    
    # This affects all axes because we set share_all = True.
    ax.set_ylim(z_axis_min,z_axis_max)    
    ax.set_xlim(0,chi_axis_max)      

    # adjust the text
    adjust_text(texts)   
    
    # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
    ax.tick_params(axis='both', width=1, pad = 2)
    for tick in ax.xaxis.get_major_ticks():
        tick.set_pad(2)       

    print "The figure format is: " + FigFormat
    if FigFormat == 'show':    
        plt.show()
    elif FigFormat == 'return':
        return fig 
    else:
        plt.savefig(newFilename,format=FigFormat,dpi=500)
        fig.clf()           
        
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
## This function plots channels, color coded in chi space with a gradient
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=        
def StackedProfilesGradient(chi_csv_fname, FigFileName = 'Image.pdf',
                       FigFormat = 'show',elevation_threshold = 0, 
                       first_basin = 0, last_basin = 0, basin_order_list = [],
                       basin_rename_list = [],
                       this_cmap = plt.cm.cubehelix,data_name = 'chi', X_offset = 5,
                       plotting_data_format = 'log',
                       label_sources = False,
                       size_format = "ESURF"):
    """This function plots the chi vs elevation or flow distance vs elevation.
    
    It stacks profiles (so the basins are spaced out).
    It colours the plots by the chi steepness (which is equal to the normalised channel steepness if A_0 is set to 1).
 
    Args:
        chi_csv_fname (str): The name (with full path and extension) of the cdv file with chi, chi slope, etc information. This file is produced by the chi_mapping_tool. 
        FigFileName (str): The name of the figure file
        FigFormat (str): The format of the figure. Usually 'png' or 'pdf'. If "show" then it calls the matplotlib show() command. 
        elevation_threshold (float): elevation_threshold chi points below this elevation are removed from plotting.
        first_basin (int): The basin to start with (but overridden by the basin list)
        last_basin (int): The basin to end with (but overridden by the basin list)       
        basin_order_list (int list): The basins to plot
        basin_rename_list (int list): A list for naming substitutions. Useful because LSDTopoTools might number basins in a way a human wouldn't, so a user can intervene in the names. 
        this_cmap (colormap): NOT USED! We now use a default colourmap but this may change.
        data_name (str): 'chi' or 'flow_distance' What to plot along the x-axis.
        X_offset (float): The offest in chi between the basins along the x-axis. Used to space out the profiles so you can see each of them.        
        plotting_data_format: NOT USED previously if 'log' use logarithm scale, but we now automatically do this. Might change later. 
        label_sources (bool): If true, label the sources.
        size_format (str): Can be "big" (16 inches wide), "geomorphology" (6.25 inches wide), or "ESURF" (4.92 inches wide) (defualt esurf). 
 
    Returns:
         Does not return anything but makes a plot.
         
    Author: SMM
    """

    import math
    import matplotlib.patches as patches

    label_size = 10

    # Set up fonts for plots
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = label_size     
   
    # make a figure 
    if size_format == "geomorphology":
        fig = plt.figure(1, facecolor='white',figsize=(6.25,5))
    elif size_format == "big":
        fig = plt.figure(1, facecolor='white',figsize=(16,9))
    else:
        fig = plt.figure(1, facecolor='white',figsize=(4.92126,3.5))

    gs = plt.GridSpec(100,100,bottom=0.25,left=0.1,right=1.0,top=1.0)
    ax = fig.add_subplot(gs[25:100,10:95])

    thisPointData = LSDMap_PD.LSDMap_PointData(chi_csv_fname) 
    thisPointData.ThinData('elevation',elevation_threshold)
    
    
    # Get the chi, m_chi, basin number, and source ID code
    if data_name  == 'chi':
        x_data = thisPointData.QueryData('chi')
        x_data = [float(x) for x in x_data]
    elif data_name == 'flow_distance':
        x_data = thisPointData.QueryData('flow distance')
        x_data = [float(x) for x in x_data]   
    else:
        print("I did not understand the data name. Choices are chi and flow distance. Defaulting to chi.")
        x_data = thisPointData.QueryData('chi')
        x_data = [float(x) for x in x_data] 

    elevation = thisPointData.QueryData('elevation')
    elevation = [float(x) for x in elevation]        
    m_chi = thisPointData.QueryData('m_chi')
    m_chi = [float(x) for x in m_chi]    
    basin = thisPointData.QueryData('basin_key')
    basin = [int(x) for x in basin] 
    source = thisPointData.QueryData('source_key')
    source = [int(x) for x in source]

    colorbarlabel = "$k_{sn}$"
    if (plotting_data_format == 'log'):
        log_m_chi = []
        for value in m_chi:
            if value < 0.1:
                log_m_chi.append(0)
            else:
                log_m_chi.append(math.log10(value))
        m_chi = log_m_chi
        colorbarlabel = "log$_{10}k_{sn}$"
    
    # Add the cubehelix colourbar    
    this_cmap = cubehelix.cmap(rot=1, reverse=True,start=3,gamma=1.0,sat=2.0)
    
    # need to convert everything into arrays so we can mask different basins
    Xdata = np.asarray(x_data)
    Elevation = np.asarray(elevation)
    M_chi = np.asarray(m_chi)
    Basin = np.asarray(basin)
    #Source = np.asarray(source)  
    
    max_basin = np.amax(Basin)
    max_X = np.amax(Xdata)
    max_Elevation = np.amax(Elevation)
    max_M_chi = np.amax(M_chi)
    min_Elevation = np.amin(Elevation)
    
    print("Max M_chi is: "+str(max_M_chi))
    
    z_axis_min = int(min_Elevation/10)*10 
    z_axis_max = int(max_Elevation/10)*10+10
    X_axis_max = int(max_X/5)*5+5
    M_chi_axis_max = max_M_chi
    
    elevation_range = z_axis_max-z_axis_min
    z_axis_min = z_axis_min - 0.075*elevation_range    
         
    plt.hold(True)


    # Now calculate the spacing of the stacks
    this_X_offset = 0
    if basin_order_list:
        basins_list = basin_order_list
        
        n_stacks = len(basins_list)
        added_X = X_offset*n_stacks
        X_axis_max = X_axis_max+added_X        
    else:
        # now loop through a number of basins
        if last_basin >= max_basin:
            last_basin = max_basin-1
    
        if first_basin > last_basin:
            first_basin = last_basin
            print("Your first basin was larger than last basin. I won't plot anything")
        basins_list = list(range(first_basin,last_basin+1))
 
        n_stacks = last_basin-first_basin+1
        added_X = X_offset*n_stacks
        print("The number of stacks is: "+str(n_stacks)+" the old max: "+str(X_axis_max))    
        X_axis_max = X_axis_max+added_X
        print("The nex max is: "+str(X_axis_max))
 
    
    # Now start looping through the basins   
    dot_pos = FigFileName.rindex('.')
    newFilename = FigFileName[:dot_pos]+'_GradientStack'+str(first_basin)+FigFileName[dot_pos:]
  
    for basin_number in basins_list:
        
        print ("This basin is: " +str(basin_number))

        m = np.ma.masked_where(Basin!=basin_number, Basin)
        maskX = np.ma.masked_where(np.ma.getmask(m), Xdata)
        maskElevation = np.ma.masked_where(np.ma.getmask(m), Elevation)
        maskMChi = np.ma.masked_where(np.ma.getmask(m), M_chi)
        #maskSource = np.ma.masked_where(np.ma.getmask(m), Source_colors)
        
        print("adding an offset of: "+str(this_X_offset))

        # Get the minimum and maximum
        this_min_x = np.nanmin(maskX)
        if this_min_x < 0:
            this_min_x = 0
        this_max_x =np.nanmax(maskX)
        width_box = this_max_x-this_min_x
        
        # Now add the offset to the minimum and maximum
        this_min_x = this_min_x+this_X_offset
        this_max_x = this_max_x+this_X_offset
        
        # Now add the offset to the data
        maskX = np.add(maskX,this_X_offset)
        this_X_offset = this_X_offset+X_offset
        
        
        
        print("Min: "+str(this_min_x)+" Max: "+str(this_max_x))
        ax.add_patch(patches.Rectangle((this_min_x,z_axis_min), width_box, z_axis_max-z_axis_min,alpha = 0.01,facecolor='r',zorder=-10))      
        
        # some logic for the basin rename
        if basin_rename_list:
            #print("Checking length, "+str(len(basin_rename_list))+" , "+str(max_basin+1))
            if len(basin_rename_list) == max_basin+1:
                this_basin_text = "Basin "+str(basin_rename_list[basin_number])
                print("This basin text is: "+this_basin_text)
        else:
            this_basin_text = "Basin "+str(basin_number) 
        
          
        ax.text(this_min_x+0.1*width_box, z_axis_min+0.025*elevation_range, this_basin_text, style='italic',
                verticalalignment='bottom', horizontalalignment='left',fontsize=8)
        if basin_number == basins_list[-1]:
            print("last basin, geting maximum value,basin is: "+str(basin_number))
            this_max = np.amax(maskX)
            this_max = int(this_max/5)*5+5
            print("The rounded maximum is: "+str(this_max))
            X_axis_max = this_max
        
        sc = ax.scatter(maskX,maskElevation,s=2.0, c=maskMChi,cmap=this_cmap,edgecolors='none')
 
    # set the colour limits
    sc.set_clim(0, M_chi_axis_max)
    #bounds = (0, M_chi_axis_max)

    # This is the axis for the colorbar
    
    ax2 = fig.add_subplot(gs[10:15,15:70])
    cbar = plt.colorbar(sc,cmap=this_cmap,spacing='uniform', orientation='horizontal',cax=ax2)   
    cbar.set_label(colorbarlabel, fontsize=10)
    ax2.set_xlabel(colorbarlabel, fontname='Arial',labelpad=-35)        

    ax.spines['top'].set_linewidth(1)
    ax.spines['left'].set_linewidth(1)
    ax.spines['right'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1) 

    
    ax.set_ylabel("Elevation (m)") 
 
    # we need special formatting for the fow distance, since we want locations in kilometres
    if data_name == 'flow_distance':
        # now get the tick marks    
        n_target_tics = 5
        X_axis_min = 0
        xlocs,new_x_labels = LSDMap_BP.TickConverter(X_axis_min,X_axis_max,n_target_tics)
        
        ax.set_xticks(xlocs)
 
        ax.set_xticklabels(new_x_labels,rotation=60)
 
        ax.set_xlabel("Flow distance (km)")        
    else:
        ax.set_xlabel("$\chi$ (m)")

   
    # This affects all axes because we set share_all = True.
    ax.set_ylim(z_axis_min,z_axis_max)    
    ax.set_xlim(0,X_axis_max)      

    # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
    ax.tick_params(axis='both', width=1, pad = 2)
    for tick in ax.xaxis.get_major_ticks():
        tick.set_pad(2)       

    print "The figure format is: " + FigFormat
    if FigFormat == 'show':    
        plt.show()
    elif FigFormat == 'return':
        return fig 
    else:
        plt.savefig(newFilename,format=FigFormat,dpi=500)
        fig.clf()                   
