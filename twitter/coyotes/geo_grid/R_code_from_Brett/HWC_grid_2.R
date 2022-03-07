#### statewide grid for HWC analysis for Isaac Lo
#### Brett Furnas, CDFW, 1/21/22




#### set up (need to install R and the library packages shown below)
library(sp)
library(rgdal)
library(rgeos)
library(raster)




#### get shapefile of California and precipitation data
setwd("C:/Users/bfurnas/Documents/Models/HWC USF 2021") # set to local
load("HWCgridData.RData")
counties<-readOGR(".","counties") # read in shapefile for counties




#### set grid size
grid.size<-10000 # 10 km (10,000 m)




#### create grid (clipped to California)
grid <- raster(extent(state.CA))
res(grid) <- grid.size
proj4string(grid)<-proj4string(state.CA)
grid <- rasterToPolygons(grid)
grid <- intersect(state.CA, grid)
grid$id<-1:length(grid)
grid$x.cen<-coordinates(grid)[,1]
grid$y.cen<-coordinates(grid)[,2]
grid$sqkm<-gArea(grid,byid=T)/(1000^2)
grid$inclusion<-grid$sqkm/(grid.size/1000)^2

plot(grid,col="yellow")
plot(state.CA,add=T,lwd=2)
length(grid) # 4351 quadrats for 10 km grid size




#### remove outlying grid quadrats beyond state boundaries based on inclusion ratio 
inclusion.ratio<-0.5 # 50% of grid is within state 
grid<-grid[which(grid$inclusion>=inclusion.ratio),]
grid$id<-1:length(grid)

plot(grid,col="blue",add=T)
length(grid) # 4090 quadrats for 10 km grid size




#### add county information to county (consider aggregating tweet collection to counties)
grid$county<-NA
for(j in 1:length(counties)){
temp.grid<-intersect(grid,counties[j,])
grid$county[temp.grid$id]<-counties$NAME_UCASE[j]
} # j

## show grid quadrats for Sacramento County
plot(grid)
plot(grid[which(grid$county=="SACRAMENTO"),],col="blue",add=T)




#### add 30-year normal average annual precipitation covariate to grid (from OSU PRISM)
grid$ppt<-NA
for(j in 1:length(grid)){
grid$ppt[j]<-mean(extract(ppt.raster,grid[j,])[[1]],na.rm=T)
}

plot(grid,col="blue")
plot(grid[which(grid$ppt>500),],col="yellow",add=T)
plot(grid[which(grid$ppt>1000),],col="red",add=T)

start<-c(100000,100000)
points(c(start[1],start[1]+200000),c(start[2],start[2]),type="l",lwd=2)
text(start[1]+100000,start[2]+50000,"200 km",cex=0.8)
start<-c(120000,430000)
text(start[1]+200000,start[2],labels="30-yr normal annual precipitation",font=2,cex=0.8)
start<-c(100000,370000)
text(start[1]+100000,start[2],labels="<500 mm",cex=0.8)
points(start[1]+300000,start[2],pch=22,bg="blue",cex=1)
start<-start-c(0,50000)
text(start[1]+100000,start[2],labels="500 - 1,000 mm",cex=0.8)
points(start[1]+300000,start[2],pch=22,bg="yellow",cex=1)
start<-start-c(0,50000)
text(start[1]+100000,start[2],labels=">1,000 mm",cex=0.8)
points(start[1]+300000,start[2],pch=22,bg="red",cex=1)




#### export csv of grid polygon
grid.out<-data.frame(id=grid$id,county=grid$county,
x.cen=grid$x.cen,y.cen=grid$y.cen,
xmin=NA,xmax=NA,ymin=NA,ymax=NA,
sqkm=grid$sqkm,inclusion=grid$inclusion,
ppt=grid$ppt)

grid.ll<-spTransform(grid,CRS(paste("+init=epsg:",4326,sep="")))

for(j in 1:length(grid)){
grid.out$xmin[j]<-xmin(grid.ll[j,])
grid.out$xmax[j]<-xmax(grid.ll[j,])
grid.out$ymin[j]<-ymin(grid.ll[j,])
grid.out$ymax[j]<-ymax(grid.ll[j,])
} # j


# write out file as csv
write.csv(grid.out,file="grid_out.csv")



#### END



