import os
import re
import time

import emoji
import pandas as pd
import numpy as np

from collections import Counter

from wordcloud import WordCloud, STOPWORDS

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords


class WhatsappFilrt:

    # =========================================================
    # READ WHATSAPP FILE
    # =========================================================

    def read_file(self, file_path):

        encodings = [
            "utf-8-sig",
            "utf-8",
            "cp1252",
            "latin-1"
        ]

        last_error = None

        for encoding in encodings:

            try:

                with open(
                    file_path,
                    "r",
                    encoding=encoding
                ) as file:

                    lines = file.readlines()

                if len(lines) == 0:
                    raise ValueError(
                        "WhatsApp file is empty."
                    )

                return lines

            except Exception as e:

                last_error = e

        raise ValueError(
            f"Unable to read WhatsApp file: {last_error}"
        )

    # =========================================================
    # PREPROCESSING
    # =========================================================

    def PreProcessing(self, file_path):

        start_time = time.time()

        lines = self.read_file(file_path)

        messages = []

        current_date = None
        current_time = None
        current_name = None
        current_chat = None

        # -----------------------------------------------------
        # WhatsApp date/time patterns
        # -----------------------------------------------------

        patterns = [

            # 12/05/2024, 10:30 pm - John: Hello
            re.compile(
                r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s*"
                r"(\d{1,2}:\d{2}(?::\d{2})?\s*[aApP][mM])"
                r"\s*-\s*"
                r"(.+?):\s*(.*)$"
            ),

            # [12/05/2024, 10:30 pm] John: Hello
            re.compile(
                r"^\[(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s*"
                r"(\d{1,2}:\d{2}(?::\d{2})?\s*[aApP][mM])\]"
                r"\s*"
                r"(.+?):\s*(.*)$"
            ),

            # 12/05/2024, 10:30 - John: Hello
            re.compile(
                r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s*"
                r"(\d{1,2}:\d{2}(?::\d{2})?)"
                r"\s*-\s*"
                r"(.+?):\s*(.*)$"
            ),

            # 12-05-2024 10:30 - John: Hello
            re.compile(
                r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+"
                r"(\d{1,2}:\d{2}(?::\d{2})?)"
                r"\s*-\s*"
                r"(.+?):\s*(.*)$"
            )
        ]

        # -----------------------------------------------------
        # Parse each line
        # -----------------------------------------------------

        for line in lines:

            line = line.rstrip("\r\n")

            matched = None

            for pattern in patterns:

                match = pattern.match(line)

                if match:

                    matched = match
                    break

            # -------------------------------------------------
            # New message
            # -------------------------------------------------

            if matched:

                # Save previous message
                if current_date is not None:

                    messages.append({
                        "Date": current_date,
                        "Time": current_time,
                        "Name": current_name,
                        "Chats": current_chat
                    })

                current_date = matched.group(1).strip()
                current_time = matched.group(2).strip()
                current_name = matched.group(3).strip()
                current_chat = matched.group(4).strip()

            # -------------------------------------------------
            # Multiline message
            # -------------------------------------------------

            else:

                if current_date is not None:

                    text = line.strip()

                    if text:

                        if current_chat:

                            current_chat += " " + text

                        else:

                            current_chat = text

        # -----------------------------------------------------
        # Save last message
        # -----------------------------------------------------

        if current_date is not None:

            messages.append({
                "Date": current_date,
                "Time": current_time,
                "Name": current_name,
                "Chats": current_chat
            })

        # -----------------------------------------------------
        # Check data
        # -----------------------------------------------------

        if not messages:

            raise ValueError(
                "No WhatsApp messages detected. "
                "Please check the exported WhatsApp TXT format."
            )

        # -----------------------------------------------------
        # Create DataFrame
        # -----------------------------------------------------

        dataset = pd.DataFrame(messages)

        # Make sure columns always exist
        required_columns = [
            "Date",
            "Time",
            "Name",
            "Chats"
        ]

        for column in required_columns:

            if column not in dataset.columns:

                dataset[column] = ""

        dataset = dataset[
            required_columns
        ]

        # -----------------------------------------------------
        # Clean values
        # -----------------------------------------------------

        for column in required_columns:

            dataset[column] = (
                dataset[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        # Remove completely empty chats
        dataset = dataset[
            dataset["Chats"].str.len() > 0
        ]

        # Reset index
        dataset.reset_index(
            drop=True,
            inplace=True
        )

        # -----------------------------------------------------
        # Print information
        # -----------------------------------------------------

        print("\n======================================")
        print("WHATSAPP DATASET CREATED")
        print("======================================")

        print(dataset.head())

        print("\nColumns:")
        print(dataset.columns.tolist())

        print("\nShape:")
        print(dataset.shape)

        print("\nExecution Time:")
        print(
            round(
                time.time() - start_time,
                4
            ),
            "seconds"
        )

        print("======================================\n")

        return dataset

    # =========================================================
    # WHOLE PROCESS
    # =========================================================

    def Wholeprocess(self, dataset):

        if dataset is None or dataset.empty:

            raise ValueError(
                "WhatsApp dataset is empty."
            )

        # Total messages
        result = len(dataset)

        # Total users
        result1 = dataset["Name"].nunique()

        return result, result1

    # =========================================================
    # WHATSAPP STATISTICS
    # =========================================================

    def statsWhatsApp(self, dataset):

        if dataset is None or dataset.empty:

            raise ValueError(
                "WhatsApp dataset is empty."
            )

        # -----------------------------------------------------
        # Message count by Date
        # -----------------------------------------------------

        date_chart = (
            dataset
            .groupby("Date")
            .size()
            .reset_index(
                name="MessageCount"
            )
        )

        # -----------------------------------------------------
        # Media messages
        # -----------------------------------------------------

        media_pattern = (
            r"<media omitted>"
            r"|image omitted"
            r"|video omitted"
            r"|gif omitted"
            r"|audio omitted"
            r"|sticker omitted"
        )

        media_count = (
            dataset["Chats"]
            .str.contains(
                media_pattern,
                case=False,
                na=False,
                regex=True
            )
            .sum()
        )

        # -----------------------------------------------------
        # Deleted messages
        # -----------------------------------------------------

        deleted_pattern = (
            r"this message was deleted"
            r"|you deleted this message"
        )

        msg_deleted_count = (
            dataset["Chats"]
            .str.contains(
                deleted_pattern,
                case=False,
                na=False,
                regex=True
            )
            .sum()
        )

        # -----------------------------------------------------
        # Voice calls
        # -----------------------------------------------------

        voice_call_count = (
            dataset["Chats"]
            .str.contains(
                "voice call",
                case=False,
                na=False
            )
            .sum()
        )

        # -----------------------------------------------------
        # Video calls
        # -----------------------------------------------------

        video_call_count = (
            dataset["Chats"]
            .str.contains(
                "video call",
                case=False,
                na=False
            )
            .sum()
        )

        # -----------------------------------------------------
        # Messages per user
        # -----------------------------------------------------

        stats = (
            dataset["Name"]
            .value_counts()
            .to_dict()
        )

        # -----------------------------------------------------
        # Percentage per user
        # -----------------------------------------------------

        total_messages = len(dataset)

        stats1 = {}

        for name, count in stats.items():

            percentage = (
                count /
                total_messages
            ) * 100

            stats1[name] = round(
                percentage,
                2
            )

        return (
            date_chart,
            int(media_count),
            int(msg_deleted_count),
            int(voice_call_count),
            int(video_call_count),
            stats,
            stats1
        )

    # =========================================================
    # SENTIMENT ANALYSIS
    # =========================================================

    def sentimentalAnalysis(self, dataset):

        if dataset is None or dataset.empty:

            return {
                "Positive": 0,
                "Negative": 0,
                "Neutral": 0
            }

        try:

            sid = SentimentIntensityAnalyzer()

        except Exception:

            import nltk

            nltk.download(
                "vader_lexicon"
            )

            sid = SentimentIntensityAnalyzer()

        positive = 0
        negative = 0
        neutral = 0

        # -----------------------------------------------------
        # Analyse every message
        # -----------------------------------------------------

        for message in dataset["Chats"]:

            text = str(message).strip()

            if not text:

                continue

            score = sid.polarity_scores(
                text
            )

            compound = score["compound"]

            if compound >= 0.05:

                positive += 1

            elif compound <= -0.05:

                negative += 1

            else:

                neutral += 1

        return {
            "Positive": positive,
            "Negative": negative,
            "Neutral": neutral
        }

    # =========================================================
    # TOPIC MODELLING
    # =========================================================

    def topicModelling(self, dataset):

        if dataset is None or dataset.empty:

            return {}, dataset

        dataset_topic = dataset.copy()

        # -----------------------------------------------------
        # Simple keyword-based topics
        # -----------------------------------------------------

        def find_topic(text):

            text = str(text).lower()

            if any(
                word in text
                for word in [
                    "happy",
                    "love",
                    "good",
                    "great",
                    "nice",
                    "awesome",
                    "excellent"
                ]
            ):

                return "Positive"

            elif any(
                word in text
                for word in [
                    "sad",
                    "bad",
                    "angry",
                    "hate",
                    "worst"
                ]
            ):

                return "Negative"

            elif any(
                word in text
                for word in [
                    "call",
                    "phone",
                    "ring"
                ]
            ):

                return "Calls"

            elif any(
                word in text
                for word in [
                    "photo",
                    "image",
                    "video",
                    "media",
                    "picture"
                ]
            ):

                return "Media"

            elif any(
                word in text
                for word in [
                    "food",
                    "eat",
                    "lunch",
                    "dinner",
                    "breakfast"
                ]
            ):

                return "Food"

            elif any(
                word in text
                for word in [
                    "college",
                    "class",
                    "exam",
                    "study",
                    "assignment"
                ]
            ):

                return "Education"

            else:

                return "General"

        dataset_topic["Topic"] = (
            dataset_topic["Chats"]
            .apply(find_topic)
        )

        topic_modelling = (
            dataset_topic["Topic"]
            .value_counts()
            .to_dict()
        )

        return (
            topic_modelling,
            dataset_topic
        )

    # =========================================================
    # WORD CLOUD
    # =========================================================

    def wordcloud(self, dataset):

        if dataset is None or dataset.empty:

            return None

        # -----------------------------------------------------
        # Combine all messages
        # -----------------------------------------------------

        text = " ".join(
            dataset["Chats"]
            .astype(str)
            .tolist()
        )

        # -----------------------------------------------------
        # Remove media messages
        # -----------------------------------------------------

        text = re.sub(
            r"<media omitted>",
            "",
            text,
            flags=re.IGNORECASE
        )

        # -----------------------------------------------------
        # Remove URLs
        # -----------------------------------------------------

        text = re.sub(
            r"https?://\S+|www\.\S+",
            "",
            text
        )

        # -----------------------------------------------------
        # Remove emojis
        # -----------------------------------------------------

        try:

            text = emoji.replace_emoji(
                text,
                replace=""
            )

        except Exception:

            pass

        # -----------------------------------------------------
        # Remove special characters
        # -----------------------------------------------------

        text = re.sub(
            r"[^A-Za-z0-9\s]",
            " ",
            text
        )

        # -----------------------------------------------------
        # Stopwords
        # -----------------------------------------------------

        try:

            stop_words = set(
                stopwords.words("english")
            )

        except Exception:

            import nltk

            nltk.download(
                "stopwords"
            )

            stop_words = set(
                stopwords.words("english")
            )

        stop_words.update(
            STOPWORDS
        )

        stop_words.update([
            "media",
            "omitted",
            "message",
            "deleted",
            "this",
            "that",
            "the",
            "you",
            "your",
            "are",
            "was",
            "were",
            "will",
            "for",
            "with",
            "have",
            "has",
            "from",
            "and",
            "but",
            "not"
        ])

        # -----------------------------------------------------
        # Generate word cloud
        # -----------------------------------------------------

        if not text.strip():

            return None

        cloud = WordCloud(
            width=1200,
            height=700,
            background_color="white",
            stopwords=stop_words,
            collocations=False
        )

        cloud.generate(text)

        # -----------------------------------------------------
        # Save output
        # -----------------------------------------------------

        output_folder = (
            "static/output_image"
        )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        output_path = os.path.join(
            output_folder,
            "wordcloud.png"
        )

        cloud.to_file(
            output_path
        )

        return output_path