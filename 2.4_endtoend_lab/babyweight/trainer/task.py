# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example implementation of code to run on the Cloud ML service.
"""

import argparse
import json
import os

import model

import tensorflow as tf

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bucket',
        help = 'GCS path to data. We assume that data is in gs://BUCKET/babyweight/preproc/',
        required = True
    )
    parser.add_argument(
        '--output_dir',
        help = 'GCS location to write checkpoints and export models',
        required = True
    )
    parser.add_argument(
        '--train_examples',
        help = 'Number of examples (in thousands) to run the training job over. If this is more than actual # of examples available, it cycles through them. So specifying 1000 here when you have only 100k examples makes this 10 epochs.',
        type = int,
        default = 5000
    )
    # TODO: Add an argument for --batch_size with a default of 512
    
    parser.add_argument(
        '--embed_size',
        help = 'Embedding size of a cross of n key real-valued parameters',
        type = int,
        default = 3
    )
    parser.add_argument(
        '--hidden_units',
        help = 'Hidden layer sizes to use for DNN feature columns -- provide space-separated layers',
        type = str,
        default = "128 32 4"
    )
    parser.add_argument(
        '--pattern',
        help = 'Specify a pattern that has to be in input files. For example 00001-of will process only one shard',
        default = 'of'
    )
    parser.add_argument(
        '--job-dir',
        help = 'this model ignores this field, but it is required by gcloud',
        default = 'junk'
    )

    args = parser.parse_args()
    arguments = args.__dict__

    # Unused args provided by service
    arguments.pop('job_dir', None)
    arguments.pop('job-dir', None)

    output_dir = arguments.pop('output_dir')
    model.BUCKET = arguments.pop('bucket')
    # TODO: set model.BATCH_SIZE  based on the command-line parameter for batch_size
    model.TRAIN_STEPS = (arguments.pop('train_examples') * 1000) / model.BATCH_SIZE
    print ("Will train for {} steps using batch_size={}".format(model.TRAIN_STEPS, model.BATCH_SIZE))
    model.PATTERN = arguments.pop('pattern')
    model.EMEBED_SIZE = arguments.pop('embed_size')
    model.HIDDEN_UNITS = [int(x) for x in arguments.pop('hidden_units').split(' ')]
    print ("Will use DNN size of {}".format(model.HIDDEN_UNITS))

    # Append trial_id to path if we are doing hptuning
    # This code can be removed if you are not using hyperparameter tuning
    output_dir = os.path.join(
        output_dir,
        json.loads(
            os.environ.get('TF_CONFIG', '{}')
        ).get('task', {}).get('trial', '')
    )

    # Run the training job
    model.train_and_evaluate(output_dir)
