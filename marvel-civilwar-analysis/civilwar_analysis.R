library("tm")
library("wordcloud")
library("gdata")

# Load tweets data.
all_captain_data <- read.csv("tweets_captain.csv")
all_ironman_data <- read.csv("tweets_ironman.csv")

# Get unique users.
captain_data <- all_captain_data[unique(all_captain_data$UserName), ]
ironman_data <- all_ironman_data[unique(all_ironman_data$UserName), ]

# Filter only tweets in one side of the war, based on tweet text and user description.
only_captain_data <- captain_data[which(!grepl("#teamironman|#timehomemdeferro|#timehomendeferro|#teamiroman|#teamiron", captain_data$Text, ignore.case = T) & !grepl("#teamironman|#timehomemdeferro|#timehomendeferro|#teamiroman|#teamiron", captain_data$UserDescription, ignore.case = T)), ]
only_ironman_data <- ironman_data[which(!grepl("#teamcap|#timecapitãoamerica|#timecapitãoamérica|#timecapitaoamerica|#teamcaptain|#teamcaptainamerica|#teamcapitain|#teamcapitainamerica", ironman_data$Text, ignore.case = T) & !grepl("#teamcap|#timecapitãoamerica|#timecapitãoamérica|#timecapitaoamerica|#teamcaptain|#teamcaptainamerica|#teamcapitain|#teamcapitainamerica", ironman_data$UserDescription, ignore.case = T)), ]

# Save Data.
write.table(only_captain_data, file = "only_captain_data.csv",row.names=FALSE, na="",col.names=T, sep=",")
write.table(only_ironman_data, file = "only_ironman_data.csv",row.names=FALSE, na="",col.names=T, sep=",")

#----------------------------------Chart 1: % of Exclusive Data per Team.----------------------------------------------------
total_tweets <- sum(length(captain_data$IdStr), length(ironman_data$IdStr))
total_exclusive_tweets <- sum(length(only_captain_data$IdStr), length(only_ironman_data$IdStr))

number_only_captain_data <- length(only_captain_data$IdStr)
number_rts_captain <- length(only_captain_data$IdStr[startsWith(only_captain_data$Text, 'rt', ignore.case=TRUE)])
number_tweets_captain <- length(only_captain_data$IdStr) - number_rts_captain
perc_number_rts_captain <- (number_rts_captain / total_exclusive_tweets) * 100
perc_number_tweets_captain <- (number_tweets_captain / total_exclusive_tweets) * 100

number_only_ironman_data <- length(only_ironman_data$IdStr)
number_rts_ironman <- length(only_ironman_data$IdStr[startsWith(only_ironman_data$Text, 'rt', ignore.case=TRUE)])
number_tweets_ironman <- length(only_ironman_data$IdStr) - number_rts_ironman
perc_number_rts_ironman <- (number_rts_ironman / total_exclusive_tweets) * 100
perc_number_tweets_ironman <- (number_tweets_ironman / total_exclusive_tweets) * 100

perc_only_captain <- (number_only_captain_data / total_tweets) * 100
perc_only_ironman <- (number_only_ironman_data / total_tweets) * 100
perc_only_both <- ((total_tweets - sum(number_only_captain_data, number_only_ironman_data)) / total_tweets) * 100

bar_values <- c(perc_only_captain, perc_only_ironman, perc_only_both) 

# Plot chart
sb <- barplot(bar_values,
        width = c(1, 1, 1),
        ylim=c(0,100), col = c("deepskyblue4", "red", "yellow"),
        main="% Total de Suporte a Cada Time",
        ylab="% tweets/retweets",
        names.arg=c("#TimeCapitão", "#TimeHomemdeFerro", "Ambos"),
        las=1
        )

text(sb, bar_values, labels = format(bar_values, 5),
     pos = 3, cex = .75)

box()


#-------------------------------------Chart 2: Tweets and Retweets for both teams.-----------------------------------------

# Declare Captain and Ironman data
x <- c(perc_number_tweets_captain, perc_number_rts_captain)
y <- c(perc_number_tweets_ironman, perc_number_rts_ironman)


# Create a two row matrix with x and y
height <- rbind(x, y)

tr <- barplot(height, 
              beside = TRUE,
              names.arg = c("Tweets", "Retweets"),
              col = c("deepskyblue4", "red"),
              main="% Tweets e Retweets para Cada Time",
              ylab="% tweets/retweets",
              ylim = c(0, 100)
              
)

tr <- barplot(height, 
              beside = TRUE,
              legend("topright", legend = c("#TimeCapitão", "#TimeHomemDeFerro"), fill = c("deepskyblue4", "red"), ncol = 1, cex = 0.75)
)

# Draw the bar values above the bars
text(tr, height, labels = format(height, 5),
     pos = 3, cex = .75)

box()


#-----------------------------------------Chart 3: Most Popular Heroes and Characters.---------------------------------------------
captain_match <- "captainamerica|captain-america|captain america|capitãoamérica|capitão-américa|capitão américa|capitãoamerica|capitão-america|capitaoamerica|capitao-america|capitao america"
ironman_match <- "ironman|iron-man|iron man|iroman|iro-man|iro man|homemdeferro|homem-de-ferro|homem de ferro"
blackwidow_match <- "blackwidow|black-widow|black widow|viúvanegra|viúva-negra|viúva negra|viuvanegra|viuva-negra|viuva negra"
spiderman_match <- "spiderman|spider-man|spider man|homemaranha|homem-aranha|homem aranha"
blackpanther_match <- "blackpanther|black-panther|black panther|panteranegra|pantera-negra|pantera negra"
vision_match <- "thevision|vision|ovisão|visão|ovisao|visao"
warmachine_match <- "warmachine|war-machine|war machine|máquinadecombate|máquina-de-combate|máquina de combate|maquinadecombate|maquina-de-combate|maquina de combate|máquinadeguerra|máquina-de-guerra|máquina de guerra|maquinadeguerra|maquina-de-guerra|maquina de guerra"
hawkeye_match <- "hawkeye|hawk-eye|hawk eye|gaviãoarqueiro|gavião-arqueiro|gavião arqueiro|gaviaoarqueiro|gaviao-arqueiro|gaviao arqueiro"
falcon_match <- "thefalcon|falcon|ofalcão|falcão"
sharoncarter_match <- "sharoncarter|sharon-carter|sharon carter"
buckybarnes_match <- "buckybarnes|bucky-barnes|bucky barnes|wintersoldier|winter-soldier|winter soldier|soldadoinvernal|soldado-invernal|soldado invernal"
scarletwitch_match <- "wandamaximoff|wanda-maximoff|wanda maximoff|scarletwitch|scarlet-witch|scarlet witch|feiticeiraescarlate|feiticeira-escarlate|feiticeira escarlate"
antman_match <- "antman|ant-man|ant man|homemformiga|homem-formiga|homem formiga"
crossbones_match <- "crossbones|cross-bones|cross bones|ossoscruzados|ossos-cruzados|ossos cruzados"
baronzemo_match <- "baronzemo|baron-zemo|baron zemo|helmutzemo|helmut-zemo|helmut zemo|heinrichzemo|heinrich-zemo|heinrich zemo"
redhulk_match <-"thunderboltross|thunderbolt-ross|thunderbolt ross|redhulk|red-hulk|red hulk|hulkvermelho|hulk-vermelho|hulk vermelho"
vasilykarpov_match <- "vasilykarpov|vasily-karpov|vasily karpov|karpov"
everettkross_match <- "everettkross|everett k. ross"

# Get number of tweets per hero.
n_t_captain <- sum(length(captain_data$IdStr[which(grepl(captain_match, captain_data$Text, ignore.case = T))]),
                      length(ironman_data$IdStr[which(grepl(captain_match, ironman_data$Text, ignore.case = T))])
)

n_t_ironman <- sum(length(captain_data$IdStr[which(grepl(ironman_match, captain_data$Text, ignore.case = T))]),
                      length(ironman_data$IdStr[which(grepl(ironman_match, ironman_data$Text, ignore.case = T))])
)

n_t_blackwidow <- sum(length(captain_data$IdStr[which(grepl(blackwidow_match, captain_data$Text, ignore.case = T))]),
                      length(ironman_data$IdStr[which(grepl(blackwidow_match, ironman_data$Text, ignore.case = T))])
                  )

n_t_spiderman <- sum(length(captain_data$IdStr[which(grepl(spiderman_match, captain_data$Text, ignore.case = T))]),
                      length(ironman_data$IdStr[which(grepl(spiderman_match, ironman_data$Text, ignore.case = T))])
)

n_t_blackpanther <- sum(length(captain_data$IdStr[which(grepl(blackpanther_match, captain_data$Text, ignore.case = T))]),
                     length(ironman_data$IdStr[which(grepl(blackpanther_match, ironman_data$Text, ignore.case = T))])
)

n_t_vision <- sum(length(captain_data$IdStr[which(grepl(vision_match, captain_data$Text, ignore.case = T))]),
                        length(ironman_data$IdStr[which(grepl(vision_match, ironman_data$Text, ignore.case = T))])
)

n_t_warmachine <- sum(length(captain_data$IdStr[which(grepl(warmachine_match, captain_data$Text, ignore.case = T))]),
                      length(ironman_data$IdStr[which(grepl(warmachine_match, ironman_data$Text, ignore.case = T))])
)

n_t_hawkeye <- sum(length(captain_data$IdStr[which(grepl(hawkeye_match, captain_data$Text, ignore.case = T))]),
                      length(ironman_data$IdStr[which(grepl(hawkeye_match, ironman_data$Text, ignore.case = T))])
)

n_t_falcon <- sum(length(captain_data$IdStr[which(grepl(falcon_match, captain_data$Text, ignore.case = T))]),
                   length(ironman_data$IdStr[which(grepl(falcon_match, ironman_data$Text, ignore.case = T))])
)

n_t_sharoncarter <- sum(length(captain_data$IdStr[which(grepl(sharoncarter_match, captain_data$Text, ignore.case = T))]),
                  length(ironman_data$IdStr[which(grepl(sharoncarter_match, ironman_data$Text, ignore.case = T))])
)

n_t_buckybarnes <- sum(length(captain_data$IdStr[which(grepl(buckybarnes_match, captain_data$Text, ignore.case = T))]),
                        length(ironman_data$IdStr[which(grepl(buckybarnes_match, ironman_data$Text, ignore.case = T))])
)

n_t_scarletwitch <- sum(length(captain_data$IdStr[which(grepl(scarletwitch_match, captain_data$Text, ignore.case = T))]),
                       length(ironman_data$IdStr[which(grepl(scarletwitch_match, ironman_data$Text, ignore.case = T))])
)

n_t_antman <- sum(length(captain_data$IdStr[which(grepl(antman_match, captain_data$Text, ignore.case = T))]),
                        length(ironman_data$IdStr[which(grepl(antman_match, ironman_data$Text, ignore.case = T))])
)

n_t_crossbones <- sum(length(captain_data$IdStr[which(grepl(crossbones_match, captain_data$Text, ignore.case = T))]),
                  length(ironman_data$IdStr[which(grepl(crossbones_match, ironman_data$Text, ignore.case = T))])
)

n_t_baronzemo <- sum(length(captain_data$IdStr[which(grepl(baronzemo_match, captain_data$Text, ignore.case = T))]),
                      length(ironman_data$IdStr[which(grepl(baronzemo_match, ironman_data$Text, ignore.case = T))])
)

n_t_redhulk <- sum(length(captain_data$IdStr[which(grepl(redhulk_match, captain_data$Text, ignore.case = T))]),
                     length(ironman_data$IdStr[which(grepl(redhulk_match, ironman_data$Text, ignore.case = T))])
)

n_t_vasilykarpov <- sum(length(captain_data$IdStr[which(grepl(vasilykarpov_match, captain_data$Text, ignore.case = T))]),
                   length(ironman_data$IdStr[which(grepl(vasilykarpov_match, ironman_data$Text, ignore.case = T))])
)

n_t_everettkross <- sum(length(captain_data$IdStr[which(grepl(everettkross_match, captain_data$Text, ignore.case = T))]),
                        length(ironman_data$IdStr[which(grepl(everettkross_match, ironman_data$Text, ignore.case = T))])
)

n_t_vector <- c(n_t_spiderman, n_t_blackwidow, n_t_vision, n_t_hawkeye, n_t_antman, n_t_blackpanther, n_t_scarletwitch,
                n_t_buckybarnes, n_t_warmachine, n_t_falcon, n_t_crossbones) / total_tweets * 100


#-------------------------------------Chart 4: Most frequent terms per team.-----------------------------------------

# Create corpus for Captain
corpus_captain <- Corpus(VectorSource( only_captain_data$Text ))

corpus_captain <- tm_map(corpus_captain, content_transformer(tolower))
corpus_captain <- tm_map(corpus_captain, removePunctuation)
corpus_captain <- tm_map(corpus_captain, removeWords, c(stopwords(kind = "pt"),"boa", "pra", "todos", "bom", "ser", "vai", "ainda", "bem"))

dtm_captain <- DocumentTermMatrix(corpus_captain)

dtm_captain_matrix <- as.matrix(dtm_captain)
frequency_terms_captain <- colSums(dtm_captain_matrix)
frequency_terms_captain <- sort(frequency_terms_captain, decreasing=TRUE)

# Create corpus for Iron Man
corpus_ironman <- Corpus(VectorSource( only_ironman_data$Text ))

corpus_ironman <- tm_map(corpus_ironman, content_transformer(tolower))
corpus_ironman <- tm_map(corpus_ironman, removePunctuation)
corpus_ironman <- tm_map(corpus_ironman, removeWords, c(stopwords(kind = "pt"),"boa", "pra", "todos", "bom", "ser", "vai", "ainda", "bem"))

dtm_ironman <- DocumentTermMatrix(corpus_ironman)

dtm_ironman_matrix <- as.matrix(dtm_ironman)
frequency_terms_ironman <- colSums(dtm_ironman_matrix)
frequency_terms_ironman <- sort(frequency_terms_ironman, decreasing=TRUE)


# Plot Histogram Frequent Terms - Captain America
barplot(as.table(frequency_terms_captain[0:20]), col = "deepskyblue3", main="Termos Mais Frequentes - Capitão", ylab="total",
        border="red", las=2)

# Plot Histogram Frequent Terms - Ironman
barplot(as.table(frequency_terms_ironman[0:20]), col = "red", main="Termos Mais Frequentes - Homem de Ferro", ylab="total",
        border="blue", las=2)

#-------------------------------------Chart 5: wordcloud for both teams.-----------------------------------------

# Build wordclouds
words_captain <- names(frequency_terms_captain)
wordcloud(words_captain[1:100], frequency_terms_captain[1:100], colors = "deepskyblue4")

words_ironman <- names(frequency_terms_ironman)
wordcloud(words_ironman[1:100], frequency_terms_ironman[1:100], colors = "red")


