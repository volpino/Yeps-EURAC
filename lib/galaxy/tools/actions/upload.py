import os
from __init__ import ToolAction
from galaxy.tools.actions import upload_common

import logging
log = logging.getLogger( __name__ )

class UploadToolAction( ToolAction ):
    def execute( self, tool, trans, incoming={}, set_output_hid = True ):
        dataset_upload_inputs = []
        for input_name, input in tool.inputs.iteritems():
            if input.type == "upload_dataset":
                dataset_upload_inputs.append( input )
        assert dataset_upload_inputs, Exception( "No dataset upload groups were found." )

        precreated_datasets = upload_common.get_precreated_datasets( trans, incoming, trans.app.model.HistoryDatasetAssociation )
        incoming = upload_common.persist_uploads( incoming )
        uploaded_datasets = upload_common.get_uploaded_datasets( trans, incoming, precreated_datasets, dataset_upload_inputs )
        upload_common.cleanup_unused_precreated_datasets( precreated_datasets )
        
        if not uploaded_datasets:
            return 'No data was entered in the upload form, please go back and choose data to upload.'
        
        json_file_path = upload_common.create_paramfile( trans, uploaded_datasets )
        data_list = [ ud.data for ud in uploaded_datasets ]
        return upload_common.create_job( trans, incoming, tool, json_file_path, data_list )
