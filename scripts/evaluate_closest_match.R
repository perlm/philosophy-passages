# script to evaluate and visualize matches

# imports
library(readr)
library(dplyr)
library(ggplot2)
library(stringr)

# for network visualzation
library(igraph)
library(ggraph)

# save a table image
library(gridExtra)

# load data set
dataset <- read_delim('/home/jason/argument/data/processed/closest_match.csv',
  col_names=c('index','id','author','title','year','passage','match_id','match_author','match_title','match_year','match_passage','score'),
  skip=1
)

dataset <- dataset %>%
  mutate(author = word(author, -1), 
         match_author = word(match_author, -1)
  )

dim(dataset)
head(dataset)
colnames(dataset)

# reorder factors for visualizations
author_order <- dataset %>%
  group_by(author) %>%
  summarise(year = mean(year)) %>%
  arrange(year) %>%
  ungroup() %>%
  pull(author)

dataset$author <- factor(dataset$author, levels=author_order)
dataset$match_author <- factor(dataset$match_author, levels=c('Plato',author_order))

# construct influence series
influence_tree <- dataset %>%
  group_by(author,match_author,year,match_year) %>%
  summarise(
    passages = n()
  ) %>%
  ungroup() %>%
  group_by(author) %>%
  mutate(passage_frac = passages / sum(passages)) %>%
  ungroup()

influence_tree %>%
  filter(passage_frac > 0.1) %>%
  ggplot(aes(x=author,y=match_author,fill=passage_frac)) +
  theme_minimal() +
  #theme_classic() +
  geom_tile() +
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) +
  scale_fill_gradient(low = "blue", high = "orange") +
  xlab('Author') +
  ylab('Influence')

# top 1 for each author
influence_1per <- influence_tree %>%
  group_by(author) %>%
  arrange(desc(passage_frac)) %>%
  top_n(1) %>%
  select(author,match_author) %>%
  print(n=1000) 

png("influence_1per.png", width = 400, height = 1000)
grid.draw(tableGrob(influence_1per))
dev.off()
##########################
# network visualization
nodes <- bind_rows(
  dataset %>%
    group_by(match_author) %>%
    summarise(match_year=mean(match_year)) %>%
    arrange(match_year),
  data.frame(match_author='Nietzsche', match_year=1844)
)

# replace year with index
nodes$match_year <- seq_len(nrow(nodes))

network <- graph_from_data_frame(
  influence_tree %>% 
    #mutate(passage_frac = log(passage_frac)) %>%
    filter(passage_frac > 0.1) %>%
    # cap extreme values (eg 100% of aristotle is definitionally plato matched)
    mutate(passage_frac = ifelse(passage_frac > 0.3,0.3,passage_frac)) %>%
    select(match_author,author,passage_frac,match_year),
  vertices = nodes, directed = TRUE)

# force layout
lay <- nodes %>%
    arrange(match_year) %>%
    transmute(x = match_year, y = 0)

# arc style
ggraph(network, layout = lay) +
  geom_edge_arc(aes(color=passage_frac,
                    width = passage_frac),
                alpha = 0.5,
                #arrow = arrow(length = unit(1, "mm")),
                end_cap = circle(6, 'mm'),
                show.legend = FALSE) +
  geom_node_text(
    aes(label = name),
    angle = 90,      # rotation
    hjust = 1,       # adjust horizontal justification after rotation
    vjust = 1,     # adjust vertical justification
    size = 2) +
  #xlab("Year") +
  theme_minimal(base_size = 12) +
  theme(
    #axis.text.x = element_text(angle = 45, hjust = 1),  # rotate
    axis.text.x=element_blank(),
    axis.ticks.y = element_blank(),
    axis.text.y = element_blank(),                      # hide y text if undesired
    panel.grid = element_blank()                       # clear grid (optional)
  ) +
  scale_edge_width_continuous(range = c(0, 3)) +
  scale_edge_colour_viridis(option='turbo') +
  xlab('') + ylab('')+
  coord_cartesian(ylim = c(-1, 15), clip = "off")


# circle style
ggraph(network, layout = "circle") +
  geom_edge_arc(aes(color=passage_frac,
                    width = passage_frac),
                strength = 0.2, # get lines inside circle
                alpha = 0.5,
                arrow = arrow(length = unit(1, "mm")),
                end_cap = circle(6, 'mm'),
                show.legend = FALSE) +
  geom_node_text(
    aes(label = name),
    size = 2) +
  #xlab("Year") +
  theme_minimal(base_size = 12) +
  theme(
    #axis.text.x = element_text(angle = 45, hjust = 1),  # rotate
    axis.text.x=element_blank(),
    axis.ticks.y = element_blank(),
    axis.text.y = element_blank(),                      # hide y text if undesired
    panel.grid = element_blank()                       # clear grid (optional)
  ) +
  scale_edge_width_continuous(range = c(0, 3)) +
  scale_edge_colour_viridis(option='turbo') +
  xlab('') + ylab('')

# node style
ggraph(network, layout = 'kk') + # + "fr") +
  geom_edge_arc(aes(color=passage_frac,
                    width = passage_frac),
                strength = 0.1,
                alpha = 0.5,
                #arrow = arrow(length = unit(0.5, "mm")),
                start_cap = circle(6, 'mm'),
                end_cap = circle(6, 'mm'),
                show.legend = FALSE) +
  geom_node_text(
    aes(label = name),
    size = 2) +
  #xlab("Year") +
  theme_minimal(base_size = 12) +
  theme(
    #axis.text.x = element_text(angle = 45, hjust = 1),  # rotate
    axis.text.x=element_blank(),
    axis.ticks.y = element_blank(),
    axis.text.y = element_blank(),                      # hide y text if undesired
    panel.grid = element_blank()                       # clear grid (optional)
  ) +
  scale_edge_width_continuous(range = c(0, 3)) +
  scale_edge_colour_viridis(option='turbo') +
  xlab('') + ylab('')

######################################################
# look at Fundamentals of the mm
# 25% Aquinas? 25% Hume?
# Then a leibniz chunk
dataset %>%
  filter(author=='Kant') %>%
  filter(title=='Fundamental Principles of the Metaphysic of Morals') %>%
  group_by(title,match_author) %>%
  summarise(
    passages = n(),
    avg_score = mean(score)
  ) %>%
  mutate(passage_frac = passages / sum(passages)) %>%
  arrange(desc(passages))

# Look at Fundemental:
# 107560 is start of preface
# 107575 is start of section 1
# 107598 is start of section 2
# 107701 is start of section 3

fundamentals_section_breaks <- c(107575, 107598, 107701)

# Visualize - doesn't seem to obviously split by section?
dataset %>%
  filter(author=='Kant') %>%
  filter(title=='Fundamental Principles of the Metaphysic of Morals') %>%
  #mutate(arb=1) %>%
  ggplot(aes(x=index,y=match_author,color=match_author)) +
  #ggplot(aes(x=index,y=match_author,color=score)) +
  geom_point(size=5) +
  theme_minimal() +
  geom_vline(xintercept = fundamentals_section_breaks, size=0.25)


matches_of_interest <- c('Aquinas','Leibniz', 'Hume','Rousseau')

tmp <- dataset %>%
  filter(author=='Kant') %>%
  filter(title=='Fundamental Principles of the Metaphysic of Morals') %>%
  mutate(section = case_when(
    index < fundamentals_section_breaks[1] ~ 'Preface',
    index < fundamentals_section_breaks[2] ~ 'Section 1',
    index < fundamentals_section_breaks[3] ~ 'Section 2',
    TRUE ~ 'Section 3'
  )
  ) %>%
  group_by(section,match_author) %>%
  summarise(passages = n()) %>%
  ungroup() %>%
  group_by(section) %>%
  mutate(passage_frac = passages/sum(passages)) %>%
  mutate(match_author = ifelse(match_author %in% matches_of_interest,as.character(match_author),'Other')) %>%
  mutate(match_author = factor(match_author, levels = c('Other',matches_of_interest))) %>%
  filter(match_author != 'Other') %>%
  mutate(match_author = factor(match_author, levels = matches_of_interest))
  

tmp %>% arrange(section,desc(passage_frac))

tmp %>%
  ggplot(aes(x=section,y=passage_frac,fill=match_author)) +
  geom_bar(stat = "identity") +
  ylab('Fraction of Passages') +
  xlab('') +
  theme_minimal() +
  ggtitle("Kant's 'Fundamental Principles of the Metaphysics of Morals'")


# evenly split among a few - tends to be hume + aquinas
dataset %>%
  filter(author=='Kant') %>%
  filter(title %in% c(
    "The Critique of Pure Reason",
    "Kant's Critique of Judgement",
    "The Critique of Practical Reason",
    "Fundamental Principles of the Metaphysic of Morals")) %>%
  group_by(title,match_author) %>%
  summarise(n=n(),score=mean(score)) %>%
  ungroup() %>%
  arrange(title,desc(n)) %>%
  group_by(title) %>%
  mutate(frac=n/sum(n)) %>%
  top_n(3)

dataset %>%
  filter(author=='Kant') %>%
  filter(title %in% c(
    "The Critique of Pure Reason",
    "Kant's Critique of Judgement",
    "The Critique of Practical Reason",
    "Fundamental Principles of the Metaphysic of Morals")) %>%
  ggplot(aes(x=score)) +
  geom_density() +
  theme_minimal() 

# not clearly distinguished by section
dataset %>%
  filter(author=='Kant') %>%
  filter(title %in% c(
    "The Critique of Pure Reason",
    "Kant's Critique of Judgement",
    "The Critique of Practical Reason",
    "Fundamental Principles of the Metaphysic of Morals"))%>%
  #filter(score>0.7) %>%
  ggplot(aes(x=index,y=match_author,color=match_author)) +
  geom_point(size=5) +
  facet_wrap(~title,scales='free_x') +
  theme_minimal() 

### Is this facile?
dataset %>%
  filter(author=='Kant') %>%
  filter(title=='Fundamental Principles of the Metaphysic of Morals') %>%
  filter(match_author %in% c('Aquinas','Hume','Rousseau','Leibniz')) %>%
  group_by(match_author) %>%
  mutate(max_score=max(score)) %>%
  ungroup() %>%
  filter(score == max_score) %>%
  write.csv("evaluate_highscore.csv", row.names = FALSE)
