library(ggplot2)
library(dplyr)
library(tidyr)

# https://www.kaggle.com/niklasdonges/end-to-end-project-with-python#Building-Machine-Learning-Models
bc5 <- read.csv("~/Documents/studium/analyse_semi_und_unstrukturierter_date/urticaria/retrieval/model_training/spacy_train_bc5.tsv", sep="\t", header = TRUE)
web <- read.csv("~/Documents/studium/analyse_semi_und_unstrukturierter_date/urticaria/retrieval/model_training/spacy_train_web.tsv", sep="\t", header = TRUE)
bc5["BASE_MODEL"] = "en_ner_bc5cdr_md"
web["BASE_MODEL"] = "en_core_web_md"
#train <- read.csv("~/Documents/studium/analyse_semi_und_unstrukturierter_date/urticaria/retrieval/model_training/spacy_train_bc5.tsv", sep="\t", header = TRUE)
train <- rbind(bc5, web)
train$ENTS_F = train$ENTS_F / 100
train$ENTS_P = train$ENTS_P / 100
train$ENTS_R = train$ENTS_R / 100
train

train %>%
  select(c(E,BASE_MODEL, ENTS_P,ENTS_R,SCORE)) %>%
  pivot_longer(!c(E,BASE_MODEL)) %>%
  ggplot(aes(E, value, colour=name)) + geom_line() +
  # ggtitle("Precision vs. Recall") +
  theme_bw() +
  xlab("Number of Epochs") +
  scale_y_continuous(name = "Value (%)", limits = c(0, 1)) +
  facet_wrap(~BASE_MODEL)

ggsave("spacy_train_precision_recall.png")

train %>%
  select(c(E, BASE_MODEL, LOSS_NER, LOSS_TOK2VEC)) %>%
  pivot_longer(!c(E,BASE_MODEL)) %>%
  ggplot(aes(E, value, colour=name)) + geom_line() +
  # ggtitle("Precision vs. Recall") +
  theme_bw() +
  xlab("Number of Epochs")  +
  facet_wrap(~BASE_MODEL)
ggsave("spacy_train_losses.png")