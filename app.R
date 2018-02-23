library(shiny)
library(leaflet)
library(readr)
library(viridis)
library(ggplot2)
library(ggvis)
library(dplyr)

sample <- read_csv("https://raw.githubusercontent.com/davidq2010/HackU/master/finalData.csv")
sample <- sample[!duplicated(sample),]
sample$label1 <- paste("<p><span ><strong><a href=\"",(sample$website),"\"><span>",sample$name,"</span></a></strong></span></p><p>google review:",sample$google_rating,"</p><p>address:",sample$address,"</p>")
sample$closest <- abs( (sample$lat - sample$lat[1] ) + (sample$lng -  sample$lng[1]))
#have a reactive number called position which tells us the current selection



# Define UI ----
ui <- navbarPage("compareURcompany", id = "nav",
  
  tabPanel("Interactive Map",              
  
  #titlePanel(h1("PowerSport Comparisons", align = "center")),
  
  sidebarLayout(
    position = "right",
    sidebarPanel("Power Sports",
                 p("Select a power sports company to see information on it. Also see its ranking relative to nearby competitors"),
                 uiOutput("value")
                 
                 
                 
    #mainPanel(img(src = "Rplot.png", width = 500), align = "center")

    
    ),
    mainPanel(
      fluidRow(leafletOutput("mymap")),
              
      fluidRow(DT::dataTableOutput("mytable2"))
              
              )
  )
  ),

  tabPanel("Data Table", 
           sidebarLayout(
             
             sidebarPanel(
             conditionalPanel(TRUE,
             checkboxGroupInput("show_vars", "Attributes:",
                   list("name", "address", "tel", "website", "google_rating"), selected = list("name", "address", "rating"))
             ),width = 2
             ),
             mainPanel(
             DT::dataTableOutput("mytable1")
             )
           
           
           )
  )

) 


# Define server logic ----
server <- function(input, output) {
  position <- reactiveVal(1)
  output$mymap <- renderLeaflet({
    leaflet(sample) %>%
      addTiles()%>%
      addMarkers(~lng,~lat, popup = ~label1)
  })
  output$mytable1 <- DT::renderDataTable({
    DT::datatable(sample[, input$show_vars, drop = FALSE])
  })
  output$mytable2 <- DT::renderDataTable({
    latitude <- input$mymap_marker_click$lat
    longtitude <- input$mymap_marker_click$lng
    if(is.null(latitude)){
      latitude = 36.8475
    }
    if(is.null(longtitude)){
      longtitude = -76.2913
    }
    {
      {sample$closest <- abs( (sample$lat - latitude ) + (sample$lng -  longtitude))}
      number <- { which(sample$closest == min(sample$closest))}
      sample2 <- subset(sample, closest < 0.1)
      sample2 <-sample2[order(-sample2$google_rating),]
    }
    DT::datatable(sample2[, input$show_vars, drop = FALSE])
  })
  #row <- {sample$closest <- abs( (sample$latitude - input$mymap_marker_click$lat ) + (sample$longtitude + input$mymap_marker_click$lng) )
  #which(sample$closest == min(sample$closest))}
  output$value <- renderText({
    latitude <- input$mymap_marker_click$lat
    longtitude <- input$mymap_marker_click$lng
    if(is.null(latitude)){
      latitude = 36.8475
    }
    if(is.null(longtitude)){
      longtitude = -76.2913
    }
    print(longtitude)
    number <- {sample$closest <- abs((sample$lat - latitude ) + (sample$lng -  longtitude) )
    which(sample$closest == min(sample$closest))}
    position({as.numeric(number)})
    sample$label1[number]
  
  })
  output$position<- renderText({
    position()                     # rv$value
  })
  #input$mymap_marker_click$lat
}



# Run the app ----
shinyApp(ui = ui, server = server)