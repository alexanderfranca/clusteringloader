import os
import pprint
import datetime
import re
import glob
import subprocess
from sqlalchemy.sql import func
from Ec import *
from ClusteringMethod import *
from Cluster import *
from Connection import *

class ClusteringLoader:
    """
    Deals with clustering results loading into relational database.

    This class is heavly attached to the relational database.

    There's no meaning for this class without a relational database connection.

    """

    def __init__(
            self,
            label=None,
            date=None,
            author=None,
            software=None,
            source_data=None,
            metadata_file=None,
            insert_files_directory=None,
            database=None,
            password=None,
            host=None,
            user=None):

        # Metadata about the clustering results
        self.label = label
        self.date = date
        self.author = author
        self.software = software
        self.source_data = source_data

        # Destination for the database insert instructions file.
        self.insert_files_directory = insert_files_directory 

        # To store what files are ok or not to be loaded into relational database. 
        self.valid_files = []
        self.invalid_files = []

        # Just for report... don't really need that.
        self.ecs_with_single_cluster = None
        self.ecs_with_two_clusters = None
        self.ecs_with_more_than_two_clusters = None

        # For relational database data control.
        self.current_cluster_primary_key = 0
        self.last_cluster_primary_key = None
        self.last_cluster_identification = None

        # Database connection parameters.
        self.user = user
        self.password = password
        self.host = host 
        self.database = database 

        # -------------------------------------------------------------------------------- #
        # Database session. We need one.                                                   #
        # -------------------------------------------------------------------------------- #
        # ---- IF YOU WANT TO REFACTOR THIS CLASS TO REMOVE DEPENDENCY, YOU ONLY HAVE ---- #
        # ---- TO PROVIDE A VALID SQLAlchemy Session and attach to the self.session   ---- #
        # -------------------------------------------------------------------------------- #
        self.session = None
        # -------------------------------------------------------------------------------- #

        c = Connection()
        self.session = c.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            database=self.database)

        if metadata_file:
            self.generate_metadata_from_file(metadata_file)

    def connection_parameters(self):
        """
        Returns data parameters used in the database connection.

        Returns:
            (dict): Data from connected database.
        """

        return {
            'database': self.database,
            'username': self.user,
            'host': self.host}

    def result_files(self):
        """
        Get the list of cluster result files.

        Returns:
            (list): List of cluster result file paths.

        """

        files = []

        files = glob.glob(self.source_data + '/*.fasta_*')

        return files

    def check_files_consistency(self):
        """
        Run through the result files and check if each one is a valid file.

        Also creates a list of valid files and a list of invalid files.

        """

        files = self.result_files()

        for my_result_file in files:

            if self.is_valid_result_file(my_result_file):
                self.valid_files.append(my_result_file)
            else:
                self.invalid_files.append(my_result_file)

    def is_valid_result_file(self, file_path=None):
        """
        Test if the cluster result file is valid (content format).

        Args:
            file_path(str): Full path for a file to be tested.

        Returns:
            (boolean): True or False.

        """

        # --------------------------------------------------------- #
        # There's a lot of ways for testing files consistency...    #
        # The problem here is to not expect too much from the file. #
        # Maybe test if organism code doesn't have more than 3 or 4 #
        # chars is a good idea... but think better: you won't come  #
        # back to this code if everything is running ok for... like #
        # 4 years. And suppose KEGG change the way of coding        #
        # organisms, but keep the idea of separating code from      #
        # protein using ':' char.                                   #
        # Worse, you are importing a different database with a      #
        # different way of coding proteins.                         #
        # You got it: this method exists here only because it's an  #
        # crucial step for the importer, but it have to be more     #
        # elaborated. At this momment is not possible to say        #
        # this method is actual implemented/done.                   #
        # But... at least it test something.                        #
        # --------------------------------------------------------- #

        errors = 0
        f = open(file_path)

        # We're going to test only the first 2 lines (totaly arbitrary number).
        counter = 1

        total_of_lines = 0

        for line in f:
            line = line.rstrip('\r\n')

            total_of_lines += 1

            expected_records = line.split(':')

            if len(expected_records) != 2:
                errors += 1

            counter += 1

            if counter == 2:
                counter = 1
                f.close()
                break

        f.close()

        if total_of_lines == 0:
            errors += 1

        if errors > 0:
            return False
        else:
            return True

    def get_valid_result_files(self):
        """
        Return the list of valid (content format) cluster result files.

        Returns:
            (list): List of valid cluster file paths.
        """

        return self.valid_files


    def generate_metadata_from_file(self, metadata_file=None):
        """
        Generate the class metadata from the results metadata file.

        Args:
            metadata_file(str): Full path for the clustering metadata file.

        """

        result_metadata = {}

        # Too busy and lazy to write an smarter approach.
        with open(metadata_file) as f:

            for line in f:
                line = line.rstrip('\r\n')

                records = line.split('=')

                if len(line) > 1:
                    field = re.sub(' ', '', records[0])

                    value = re.sub('^ ', '', records[1])
                    value = re.sub(' $', '', value)

                    result_metadata[field] = value

        self.author = result_metadata['author']
        self.label = result_metadata['label']
        self.date = result_metadata['date']
        self.software = result_metadata['software']
        self.source_data = result_metadata['clusters']

    def total_valid_files(self):
        """
        Return the total of valid cluster result files.

        Returns:
            (int): Total of valid files.

        """

        return len(self.valid_files)

    def total_invalid_files(self):
        """
        Return the total of invalid cluster result files.

        Returns:
            (int): Total of invalid files.

        """

        return len(self.invalid_files)

    def ec_number_from_file_name(self, file_path=None):
        """
        Return the EC number from the cluster result file name.

        Return:
            (str): EC number.

        """

        file_name = os.path.basename(file_path)

        # EC_4.2.1.51.fasta_2

        ec_number = re.search('^EC_(.*)\.fasta_.*', file_name)

        ec_number = str(ec_number.group(1))

        return ec_number

    def ec_numbers(self):
        """
        Return the total of EC numbers found in the cluster result files.

        Returns:
            (int): Total of EC numbers.

        """

        ec_numbers = []

        files = self.result_files()

        for result_file in files:
            ec_number = self.ec_number_from_file_name(result_file)

            ec_numbers.append(ec_number)

        return ec_numbers

    def total_ec_numbers(self):
        """
        Return the total of EC numbers found in the cluster result files.

        Returns:
            (int): Total of EC numbers.

        """

        return len(self.ec_numbers())

    def total_sequences(self):
        """
        Return the total of sequences found in all cluster result files.

        Returns:
            (int): Total of sequences.

        """

        total_of_sequences = 0

        self.check_files_consistency()

        files = self.valid_files

        for result_file in files:

            with open(result_file) as f:

                for line in f:
                    total_of_sequences += 1

        return total_of_sequences

    def cluster_identification_from_file(self, file_path=None):
        """
        Get the cluster identification form a result file.

        Normally it's only a single integer.

        Args:
            file_path(str): File path or only file name.

        Returns:
            (str): Cluster identification from result file.

        """

        file_name = os.path.basename(file_path)

        cluster_id = re.search('^EC_.*\.fasta_(.*)', file_name)
        cluster_id = cluster_id.group(1)

        return cluster_id

    def total_clusters(self):
        """
        Return the total of clusters generated from all the clustering process.

        Returns:
            (int): Total of clusters.

        """

        clusters = []

        self.check_files_consistency()

        files = self.valid_files

        for result in files:
            clusters.append(self.cluster_identification_from_file(result))

        return len(clusters)

    def generate_ecs_clusters_stats(self):
        """
        Generate the statistics for EC numbers and its clusters.

        Returns:
            (dict): EC numbers and its clusters statistics.

        """

        self.check_files_consistency()

        ecs_with_single_cluster = []
        ecs_with_two_clusters = []
        ecs_with_more_than_two_clusters = []

        ecs_and_clusters = {}

        files = self.valid_files

        for result in files:
            ec_number = self.ec_number_from_file_name(result)

            if ec_number not in ecs_and_clusters:
                ecs_and_clusters[ec_number] = []

            cluster_identification = self.cluster_identification_from_file(
                result)

            ecs_and_clusters[ec_number].append(cluster_identification)

        for ec, total_clusters in ecs_and_clusters.iteritems():

            total_clusters = total_clusters[0]

            if int(total_clusters) == 1:
                ecs_with_single_cluster.append(ec)

            if int(total_clusters) == 2:
                ecs_with_two_clusters.append(ec)

            if int(total_clusters) > 2:
                ecs_with_more_than_two_clusters.append(ec)

        self.ecs_with_single_cluster = ecs_with_single_cluster
        self.ecs_with_two_clusters = ecs_with_two_clusters
        self.ecs_with_more_than_two_clusters = ecs_with_more_than_two_clusters

        return {
            'single': ecs_with_single_cluster,
            'two': ecs_with_two_clusters,
            'more': ecs_with_more_than_two_clusters}

    # TODO: test
    def ecs_and_its_clusters(self):
        """
        Return the EC numbers and its clusters from flat/raw cluster result files.

        Returns:
            (dict): EC numbers and its cluster numbers.

        """

        ecs_and_clusters = {}

        self.check_files_consistency()

        files = self.valid_files

        for result in files:

            ec_number = self.ec_number_from_file_name(result)

            if ec_number not in ecs_and_clusters:
                ecs_and_clusters[ec_number] = []

            cluster_identification = self.cluster_identification_from_file(
                result)

            ecs_and_clusters[ec_number].append(cluster_identification)

            # Remove duplicates
            ecs_and_clusters[ec_number] = set(ecs_and_clusters[ec_number])
            ecs_and_clusters[ec_number] = list(ecs_and_clusters[ec_number])

        return ecs_and_clusters

    # TODO: test, comments
    #      This method exists only for the testings.
    def add_clustering_method(
            self,
            name=None,
            software=None,
            date=None,
            author=None):

        c = ClusteringMethod()
        c.name = name
        c.software = software
        c.date = date
        c.author = author

        self.session.add(c)
        self.session.commit()

    # TODO: test, comment
    def clustering_method_id_from_name(self, name=None):

        result = self.session.query(
            ClusteringMethod).filter_by(name=name).first()

        return result.id

    def clustering_method_exists(self, label=None):
        """
        Check if the clustering method exists in the relational database.

        Args:
            label(str): Label/name of the clustering method.

        Returns:
            (boolean): True of False
        """

        return self.session.query(
            ClusteringMethod).filter_by(name=label).first()

    def save_metadata(self, label=None, author=None, software=None, date=None):
        """
        Save metadata into the relatinal database.

        Means create a new record for clustering_methods.

        """

        if not self.clustering_method_exists(self.label):
            c = ClusteringMethod()
            c.name = label
            c.software = software
            c.date = date
            c.author = author

            self.session.add(c)
            self.session.commit()

    def clustering_method_id(self):
        """
        Return the previously saved record in the clustering_methods.

        Returns:
            (int): Clustering method database id.

        """

        result = self.session.query(
            ClusteringMethod).filter_by(name=self.label).first()

        return result.id

    def get_last_cluster_identification(self):
        """
        Set the last cluster identification found in the relational database.

        That's important to generate the ids for the insert files.

        """

        if not self.last_cluster_identification:

            # Solve querying database.
            result_db = self.session.query(func.max(Cluster.identification))
            result_db = result_db.one()
            result_db = result_db[0]

            if result_db:
                result = result_db
            else:
                result = 0

        else:
            result = self.last_cluster_identification

        return result

    def generate_cluster_next_identification(self):
        """
        Increment table 'clusters' identification column.

        Returns:
            (int): Next cluster identification.

        """

        if not self.last_cluster_identification:
            current = self.get_last_cluster_identification()
        else:
            current = self.last_cluster_identification

        result = current + 1

        self.last_cluster_identification = result

        return result

    def get_last_cluster_id(self):
        """
        Return the last cluster id (primary key) to be used in the relational database.

        That's important to generate the ids for the insert files.

        Returns:
            (int): Last cluster id to be used.

        """

        if not self.last_cluster_primary_key:

            # Solve querying database.
            result_db = self.session.query(func.max(Cluster.id))
            result_db = result_db.one()
            result_db = result_db[0]

            if result_db:
                result = result_db
            else:
                result = 0

        else:
            result = self.last_cluster_primary_key

        return result

    def generate_cluster_next_id(self):
        """
        Increment table 'clusters' primary key id.

        Returns:
            (int): Next primary key id.

        """

        if not self.last_cluster_primary_key:
            current = self.get_last_cluster_id()
        else:
            current = self.last_cluster_primary_key

        result = current + 1

        self.last_cluster_primary_key = result

        return result

    def protein_id(self, protein_identification=None):
        """
        Return the relational database id (table 'proteins') related to the protein identification queried.

        Args:
            protein_identification(str): Protein identification in the relational database.

        Returns:
            (int): Protein database id.

        """

        result = self.session.query(Protein).filter_by(
            identification=str(protein_identification)).first()

        if result:
            return result.id

    def ec_number_id(self, ec_number=None):
        """
        Return the relational database id (table 'ecs') related to the EC number queried.

        Args:
            ec_number(str): EC number to be queried in the relational database.

        Returns:
            (int): EC number database id.

        """

        result = self.session.query(Ec).filter_by(ec=str(ec_number)).first()

        if result:
            return result.id

    def generate_insert_file(self):
        """
        Generate the clusters insert files to be loaded into the relational database.

        """

        if not self.clustering_method_exists(self.label):
            self.add_clustering_method(
                name=self.label,
                software=self.software,
                date=self.date,
                author=self.author)

        clustering_method_id = self.clustering_method_id_from_name(self.label)

        self.check_files_consistency()

        file_name_destination = self.insert_files_directory + '/' + 'clustersInsert.psql'

        if os.path.exists(file_name_destination):
            os.remove(file_name_destination)

        ecs_and_its_clusters = self.ecs_and_its_clusters()

        with open(file_name_destination, 'a') as file_destination:

            for ec, clusters in ecs_and_its_clusters.iteritems():

                ec_id = self.ec_number_id(str(ec))

                for cluster in clusters:
                    # Remount the source cluster file name in order to read the
                    # file results.
                    file_to_read = self.source_data + '/EC_' + \
                        str(ec) + '.fasta_' + str(cluster)

                    with open(file_to_read) as f:

                        cluster_identification = self.generate_cluster_next_identification()

                        for line in f:
                            line = line.rstrip('\r\n')
                            line = line.lower()

                            cluster_id = self.generate_cluster_next_id()

                            protein_id = self.protein_id(line)

                            if protein_id:
                                data = [
                                    str(cluster_id),
                                    str(cluster_identification),
                                    str(ec_id),
                                    str(protein_id),
                                    str(clustering_method_id)]

                                self.write_insert_file(file_destination, data)

                                data = []

    def write_insert_file(self, file_handle=None, data=None):
        """
        Actual write the insert instructions file that'll be inserted later into the realational database.

        Args:
            file_handle(file): File to store the data.
            data(list): List of values to insert into file.

        """

        values = '\t'.join(data)

        file_handle.write(values + "\n")

    def check_psql_can_execute_command(self):
        """
        Check if this loader can execute 'psql' commands.

        If not... nothing is going to work.

        Returns:
            (boolean): True (you can do stuff in PostgreSQL), False (you're screwed, call for help, it's a loader, don't expect to be happy here. You not even know if at this moment you're really using PostgreSQL).

        """

        # Database user name from the configuration file.
        username = self.user

        # This command only list the tables from the database.
        command = 'psql -U ' + username + " -c '\dt'"

        result = subprocess.call(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        # Zero means (from the subprocess package) the command could be
        # executed without errors.
        if result == 0:
            return True
        else:
            return False

    def load_file(self):
        """
        This is the serious business.

        This methos insert into the relational database all the result data.

        """

        if not self.check_psql_can_execute_command():
            print("ERROR:")
            print(
                "I cannot execute 'psql' command properly, so I won't try to load data.")
            print("Maybe it means you don't have a properly $HOME/.pgpass correct file.")
            print(
                "Try to create in you $USER directory a file .pgpass with the following data: ")
            print("localhost:5432:kegg2017:darkmatter")
            print(
                "BUT it's only a suggestion. Call your database administrator to know what it is.")
            sys.exit()

        username = self.user
        source_file_name = self.insert_files_directory + '/' + 'clustersInsert.psql'

        if not os.path.exists(source_file_name):
            print(source_file_name + ' file not found.')
            sys.exit()

        columns = [
            'id',
            'identification',
            'ec_id',
            'protein_id',
            'clustering_method_id']
        table = 'clusters'

        # ------------------------------------------------------------------------ #
        # ---------------- THAT'S THE STUFF WE'RE LOOKING FOR -------------------- #
        # ------------------------------------------------------------------------ #
        # This part of the code actual inserts the data into relational database   #
        # ------------------------------------------------------------------------ #
        # Columns names are being put together as a list of columns (psql
        # needed).
        columns = ','.join(columns)

        # Actual execute the command that inserts the data into relational
        # database.
        process = subprocess.Popen(
            "psql -U " +
            username +
            " -c \"\copy " +
            table +
            "(" +
            columns +
            ") from \'" +
            source_file_name +
            "\';\"",
            shell=True)

        # Things got crazy here. Some table delays a lot to be inserted and the process keep going overwhelming the next process.
        # So we wait to make sure the tables order insertions are correct.
        process.wait()
        # ------------------------------------------------------------------------ #
        # ---------------- END OF THE POPULATING PROCESS ------------------------- #
        # ------------------------------------------------------------------------ #
