import time
import os
import datetime

import pymysql
from natsort import natsorted

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from RSC_main_test_v5 import Getting_Score_Result
from django.utils import timezone
from distutils.dir_util import copy_tree
# database connection
# connection = pymysql.connect(host="172.24.171.78", port=3303,user="root",passwd="Root123",database="CopyEdit_RSC_dev" ) External use
connection = pymysql.connect(host="mysql_container", port=3306, user="dbadmin", passwd="dbadmin123", database="CopyEdit_RSC_dev")  # Internal Use
cursor = connection.cursor()


# Global declaration of operation folder
ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = "/SPLITED-DOCS/"
DIR_TO_WATCH = ROOT_FOLDER+"/Input_watcher/"
EASY_DIR = ROOT_FOLDER+OUTPUT_DIR+"EASY/"
INTERMEDIATE_DIR = ROOT_FOLDER+OUTPUT_DIR+"INTERMEDIATE/"
DIFFICULT_DIR = ROOT_FOLDER+OUTPUT_DIR+"DIFFICULT/"

# Auto Folder creation Process
if not os.path.exists(EASY_DIR):
    os.makedirs(EASY_DIR)

if not os.path.exists(INTERMEDIATE_DIR):
    os.makedirs(INTERMEDIATE_DIR)

if not os.path.exists(DIFFICULT_DIR):
    os.makedirs(DIFFICULT_DIR)


# database_insert operation
def _database_insert_operation(path):
    try:
        print("inside trying block")
        for fname in natsorted(os.listdir(path)):
            if fname.endswith(('.doc', '.docx')):
                print("file name -->", fname)
                #print("abspath name -->",(os.path.abspath(fname)))
                folder_path = path
                abs_file_path = path+'/'+fname
                result_df, file_topic_df = Getting_Score_Result(folder_path, abs_file_path)

                # if (result_df['No of words'][0] == 0 and result_df['Journal code'][0] == 0 and result_df['author nation'][0] == 0 ):
                # 	print("error handling..")
                # 	expect_top = '0'
                # 	obtain_top = '0'
                # else:
                # 	print("normal case..")

                # .format('2019-01-14 00:00:00.000000', 'fname_1', 'title_fname' )
                topic_insert_cmd = "INSERT INTO appserver_document (uploaded_at, is_edit, abstract, expect_topic, name, obtain_topic, title, modified_at, file_path) VALUES (%s, '0', %s, %s, %s, %s, %s, NULL, %s);"
                topic_insert_val = (datetime.datetime.now(tz=timezone.utc), str(file_topic_df['Abstract'][0]).encode('ascii', 'ignore').decode('ascii'), str(result_df['Topic'][0]),  str(
                    file_topic_df['File Name'][0]), str(result_df['Topic'][0]), str(file_topic_df['Title'][0]).encode('ascii', 'ignore').decode('ascii'), path)

                cursor.execute(topic_insert_cmd, topic_insert_val)
                doc_id = cursor.lastrowid
                print("doc_id -->", doc_id, type(doc_id))
                # print("result_df column types -->",type(result_df['Lang/Grammar'][0]),type(result_df['No of words'][0]), type(result_df['Journal code'][0]),type(result_df['author nation'][0]),type(result_df['article type'][0]),type(result_df['Obtained Level'][0]))

                score_insert_cmd = "INSERT INTO appserver_overallscore (grammer_language,no_of_words,journal_title,author_nationality,article_type,score,created_at,document_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
                score_insert_val = (str(result_df['Lang/Grammar'][0]), str(result_df['No of words'][0]), str(result_df['Journal code'][0]),
                                    str(result_df['author nation'][0]), str(result_df['article type'][0]), result_df['Obtained Level'][0], datetime.datetime.now(), doc_id)

                try:
                    cursor.execute(score_insert_cmd, score_insert_val)
                    score_id = cursor.lastrowid

                except Exception as e:
                    print("\n error in db execute ---> ", e)

                print("score id --->", score_id)

                connection.commit()

                print(".....db committed success.....")

                INP_DIR = path.split('/')[-1]

                if result_df['Obtained Level'][0] == "EASY":
                    copy_tree(path, EASY_DIR+INP_DIR+'/')

                elif result_df['Obtained Level'][0] == "INTERMEDIATE":
                    copy_tree(path, INTERMEDIATE_DIR+INP_DIR+'/')

                elif result_df['Obtained Level'][0] == "DIFFICULT ":
                    copy_tree(path, DIFFICULT_DIR+INP_DIR+'/')

                else:
                    pass

        print(" insert operation success...")
        return True

    except:
        print("inside exception call...")
        return False

# database delete operation


def _database_delete_operation(path):
    print("delete path --->", path)
    try:
        try:
            for fname in natsorted(os.listdir(path)):
                print("file name -->", fname)

        except FileNotFoundError:
            get_doc_id = "SELECT id FROM appserver_document WHERE file_path = %s"
            doc_path_val = (path)
            cursor.execute(get_doc_id, doc_path_val)
            doc_id = cursor.fetchall()
            parent_dir = False

            # root directory file detection
            if len(doc_id) == 0:
                get_doc_id = "SELECT id FROM appserver_document WHERE file_path LIKE '"+path+"%'"
                #print("get_root_dir -->", get_doc_id)
                #doc_path_val = (path)
                #cursor.execute(get_doc_id, doc_path_val)
                cursor.execute(get_doc_id)
                doc_id = cursor.fetchall()
                parent_dir = True

            print("doc_id --->", doc_id)
            for d_id in doc_id:
                delete_score = "DELETE FROM appserver_overallscore WHERE document_id = %s"
                cursor.execute(delete_score, d_id[0])

            if parent_dir:
                delete_cmd = "DELETE FROM appserver_document WHERE file_path LIKE '"+path+"%'"
                cursor.execute(delete_cmd)

            else:
                delete_cmd = "DELETE FROM appserver_document WHERE file_path = %s"
                delete_val = (path)
                cursor.execute(delete_cmd, delete_val)

            connection.commit()
        print(" delete operation success...")
        return True

    except:
        return False


# Watcher script class
class Watcher:
    #DIR_TO_WATCH = "/home/shantakumar/Projects/context_copy_edit_RAC/sample_watcher/"

    print("dir to watch -->", DIR_TO_WATCH)

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, DIR_TO_WATCH, recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(5)

        except:
            self.observer.stop()
            print("error in observer")

        self.observer.join()

# Event handler class


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            if event.event_type == 'created':
                # time.sleep(3)
                db_status = _database_insert_operation(event.src_path)
                # print(event.event_type,"-->", db_status)

            elif event.event_type == 'deleted':
                # time.sleep(3)
                db_status = _database_delete_operation(event.src_path)

            # return None

        # elif event.event_type == 'created':
        # 	# Take any action here when a file is first created.
        # 	print("Received created event - %s." % event.src_path)

        # elif event.event_type == 'modified':
        # 	# Taken any action here when a file is modified.
        # 	print("Received modified event - %s." % event.src_path)

        # elif event.event_type == 'deleted':
        # 	# Taken any action here when a file is deleted.
        # 	print("Received deleted event - %s." % event.src_path)


# main function
if __name__ == '__main__':
    w = Watcher()
    w.run()
