import re


class Locater:
    def __init__(self, base_id, drive, base_path):
        self.drive = drive
        self.base_id = base_id
        self.base_name = re.split('/', base_path)[-1]

    def find(self, full_path, previous_folder, previous_path):
        path_location = 0

        folder_located = False

        # Because we have a reference to the previous folder located and its ID, we try to start the search
        # from where that search left off
        if previous_path is not None:
            if previous_path in full_path:
                full_path = full_path[len(previous_path):]
                folder_id = previous_folder
                if full_path == "":
                    folder_located = True
            else:
                folder_id = self.base_id
        else:
            folder_id = self.base_id

        path_delimited = re.split('/', full_path)

        # Determining where is the list of subfolders the basefolder is located, only happens once
        if not folder_located:
            for i in range(len(path_delimited)):
                if path_delimited[i] == self.base_name:
                    path_location = i
                    break

            # If there are additional folders in the path, they are iterated through
            # Because the current folder_ID is the base folder, we start by searching folder that have this as parent

            for i in range(path_location + 1, len(path_delimited)):
                folder_located = False
                page_token = None

                response = self.drive.service.files().list(q="mimeType='application/vnd.google-apps.folder'"
                                                             and "'%s' in parents" % folder_id
                                                             and "name='%s'" % path_delimited[i],
                                                           spaces='drive',
                                                           fields='nextPageToken, files(id, name,parents)',
                                                           pageToken=page_token).execute()

                for folder in response.get('files', []):

                    print(folder.get('name'))
                    if folder.get('name') == path_delimited[i] and folder_id in folder.get('parents'):
                        folder_id = folder.get('id')
                        folder_located = True
                        print("Folder located")
                        break

                if not folder_located:
                    print("Creating folder " + path_delimited[i])
                    folder_metadata = {
                        'parents': [folder_id],
                        'name': path_delimited[i],
                        'mimeType': 'application/vnd.google-apps.folder'
                    }

                    folder = self.drive.service.files().create(body=folder_metadata,
                                                               fields='name, id,parents').execute()
                    folder_id = folder.get('id')

        return folder_id
