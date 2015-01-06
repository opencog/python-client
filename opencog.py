"""
Defines an interface to allow ECAN attention allocation experiments to be
written as short Python scripts.

See README.md for documentation and instructions.
"""

__author__ = 'Cosmo Harrigan'

from configuration import *
import os
from subprocess import check_call, Popen
from multiprocessing import Process


class Atom(object):
    """
    Stores an atom handle and an STI value

    Represents the STI value of an atom at a particular point in time.
    Intended to be contained in a PointInTime object with a timestep value.
    """
    def __init__(self):
        self.handle = None
        self.sti = None


def create_point(timestep, atoms, scheme=None):
    """
    Create a PointInTime dictionary from a JSON atom representation

    Represents a discrete point in time in a time series from an experiment
    with the ECAN attention allocation discrete dynamical system

    Each point in time contains:

    - a list of "atoms" which consists of a list of objects of type Atom
      (Refer to the definition of the Atom object)
    - an integer "timestep"
    - (optional) A Scheme representation of the point in time
    """

    atom_list = []

    for atom in atoms:
        data = {
            'handle': atom['handle'],
            'sti': atom['attentionvalue']['sti']
        }
        atom_list.append(data)

    point = {
        'timestep': timestep,
        'atoms': atom_list,
        'scheme': scheme
    }

    return point

def shell(command):
    """
    Send a command to the CogServer shell
    """
    data = {'command': command + '\n'}

    post(uri + 'shell', data=json.dumps(data), headers=headers)


def scheme(command):
    """
    Send a Scheme command to the Scheme interpreter
    """
    data = {'command': command + '\n'}

    result = post(uri + 'scheme', data=json.dumps(data), headers=headers)
    return result.json()['response']


def load_scheme_files(files):
    """
    Loads a list of Scheme files into the cogserver
    """
    for datafile in files:
        command = "(load-scm-from-file \"" + \
                  OPENCOG_SOURCE_FOLDER + datafile + "\")"
        scheme(command)


def load_python_agent(path):
    """
    Load an arbitrary Python MindAgent in the CogServer

    Parameters:
    path (required) Relative path to the agent, including the filename,
      without the file extension

    Example of 'path':
      ../opencog/python/pln/examples/tuffy/smokes/smokes_agent
    """
    arg = "loadpy {0}".format(path)
    shell(arg)


def start_python_agent(path, name):
    """
    Start a Python MindAgent that has already been loaded

    Parameters:
    path (required) Relative path to the agent, including the filename,
      without the file extension

    Example of 'path':
      ../opencog/python/pln/examples/tuffy/smokes/smokes_agent

    name (required) Name of the agent

    Example of 'name':
      InferenceAgent
    """
    arg = "agents-start {0}.{1}".format(path, name)
    shell(arg)


def step_agent(name):
    """
    Run a step of an arbitrary C++ agent in the CogServer

    Parameters:
    name (required) Name of the agent

    Example of 'name':
      SimpleImportanceDiffusionAgent
    """
    arg = "agents-step opencog::{0}".format(name)
    shell(arg)


def step_python_agent(path, name):
    """
    Run a step of an arbitrary Python agent in the CogServer

    Parameters:
    path (required) Relative path to the agent, including the filename,
      without the file extension
    name (required) Name of the agent

    Example of 'path':
      ../opencog/python/pln/examples/tuffy/smokes/smokes_agent
    Example of 'name':
      InferenceAgent
    """
    arg = "agents-step opencog::PyMindAgent({0}.{1})".format(path, name)
    shell(arg)


def get_attentional_focus(timestep, scheme=False):
    """
    Get the atoms in the attentional focus

    Parameters:
    timestep (required) You should provide a monotonically increasing timestep
      value to uniquely identify the timestep of this attentional focus
      snapshot.
    scheme (optional) If True, the Scheme representation of the attentional
      focus will also be captured. Default is False.
    """
    get_response = get(uri + 'atoms?filterby=attentionalfocus')
    get_result = get_response.json()['result']['atoms']

    if not scheme:
        return create_point(timestep, get_result)
    else:
        af_contents = dump_attentional_focus_scheme()
        return create_point(timestep, get_result, scheme=af_contents)


def get_atomspace(timestep, scheme=False):
    """
    Take a snapshot of the atomspace at a given point in time

    :param timestep: an integer representing a monotonically increasing
    timestep value which identifies the timestep of this atomspace snapshot
    :param scheme: If True, the Scheme representation of the atomspace will
    also be captured.
    :return: a PointInTime dictionary that captures the atomspace at the given
    timestep
    """
    get_response = get(uri + 'atoms')
    get_result = get_response.json()['result']['atoms']

    if not scheme:
        return create_point(timestep, get_result)
    else:
        atomspace_contents = dump_atomspace_scheme()
        return create_point(timestep, get_result, scheme=atomspace_contents)


def atomspace():
    """
    Retrieves a snapshot of the atomspace. Take note that the snapshot returned
    is static, and must be called again when you want it to be updated.
    :return: a dictionary of atoms
    """
    get_response = get(uri + 'atoms')
    get_result = get_response.json()['result']['atoms']

    result = {}
    for atom in get_result:
        result[atom['handle']] = atom

    return result


def export_timeseries_csv(timeseries, filename, scheme=False):
    """
    Export the timeseries to a CSV file.

    Parameters:
    timeseries (required) The timeseries that will be exported.
    filename (required) The name of the file that will be written to.
    scheme (optional) If True, the full Scheme representation of the point in
      in time will be included with each row. Defaults to False.

    Format:
    time, handle, sti

    If the timeseries contains a Scheme representation, the format is:
      time, handle, sti, scheme
    """
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for point in timeseries:
            for atom in point['atoms']:
                if point['scheme'] is not None and scheme is True:
                    writer.writerow([point['timestep'],
                                     atom['handle'],
                                     atom['sti'],
                                     point['scheme']])
                else:
                    writer.writerow([point['timestep'],
                                     atom['handle'],
                                     atom['sti']])


def export_timeseries_mongodb(timeseries):
    """
    Export the timeseries to a MongoDB database.

    Parameters:
    timeseries (required) The timeseries that will be exported.
    """
    clear_mongodb()
    mongo['points'].insert(timeseries)


def dump_atomspace_scheme():
    """
    Returns all atoms in the atomspace in Scheme format
    """
    return scheme("(cog-prt-atomspace)")


def dump_atomspace_dot():
    """
    Returns all atoms in the atomspace in DOT graph description language
    format
    """
    get_response = get(uri + 'atoms?dot=True')
    get_result = get_response.json()['result']
    return get_result


def dump_attentional_focus_scheme():
    """
    Returns all atoms in the attentional focus in Scheme format
    """
    return scheme("(cog-af)")


def clear_atomspace():
    """
    Clear the atomspace
    """
    scheme("(clear)")


def stop_agent_loop():
    """
    Stop the automatic stepping of agents in the CogServer, so that agents
    can be stepped manually
    """
    shell("agents-stop-loop")


def set_af_boundary(value):
    """
    Set the AttentionalFocusBoundary

    Parameters:
    value The STI value to set the AttentionalFocusBoundary to
    """
    arg = "(cog-set-af-boundary! {0})".format(value)
    scheme(arg)


def importance_diffusion():
    """
    Run a step of the simple importance diffusion agent
    """
    step_agent("SimpleImportanceDiffusionAgent")


def importance_updating():
    """
    Run a step of the importance updating agent
    """
    step_agent("ImportanceUpdatingAgent")


def hebbian_updating():
    """
    Run a step of the hebbian updating agent
    """
    step_agent("HebbianUpdatingAgent")


def forgetting():
    """
    Run a step of the forgetting agent
    """
    step_agent("ForgettingAgent")


def set_diffusion_percent(value):
    """
    Sets the diffusion percentage parameter for the attention allocation
    importance diffusion agent
    :param value: Probability value between 0 and 1 representing the percentage
    of an atom's STI that should be diffused at each step
    """
    scheme('(EvaluationLink (PredicateNode "CONFIG-DiffusionPercent") '
           '(ListLink (NumberNode "{0}")))'.format(value))


def set_stimulus_amount(value):
    """
    Sets the stimulus amount parameter for the PLN reasoning agent
    :param value: Integer value representing the amount of stimulus to be
    assigned to the target
    """
    scheme('(EvaluationLink (PredicateNode "CONFIG-StimulusAmount") (ListLink '
           '(NumberNode "{0}")))'.format(value))


def set_rent(value):
    """
    Sets the rent parameter for the attention allocation importance updating
    agent
    :param value: Integer value representing the amount of stimulus to be
    assigned to the target
    """
    scheme('(EvaluationLink (PredicateNode "CONFIG-Rent") (ListLink '
           '(NumberNode "{0}")))'.format(value))


def set_wages(value):
    """
    Sets the wages parameter for the attention allocation importance updating
    agent
    :param value: Integer value representing the amount of stimulus to be
    assigned to the target
    """
    scheme('(EvaluationLink (PredicateNode "CONFIG-Wages") (ListLink '
           '(NumberNode "{0}")))'.format(value))


def relex(sentence, display=True, concise=True):
    """
    :param sentence: The sentence to send to RelEx for parsing
    :param display: Whether to print the output (default=True)
    :param concise: Whether to strip status messages from the output (default=True)
    :return: Human-readable parse of the sentence
    """
    if USE_VAGRANT:
        result = run_vagrant_command(
            VAGRANT_ID_RELEX, 'cd /home/vagrant/relex && ./relex.sh 1 "" "' + sentence + '"')
        if concise:
            result = result.split("Parse 1 of 1", 1)[1]
            result = result.rpartition("======")[0]
            result = result.strip()

        if display:
            print result
        else:
            return result


def to_logic(sentence, clear=True, display=True):
    """
    :param sentence: The sentence to send to RelEx2Logic for parsing
    :param clear: Whether to clear the atomspace before processing (default=True)
    :param display: Whether to print the output (default=True)
    :return: Contents of the SetLink representing the parsed sentence
    """
    if clear:
        scheme("(clear)")
    scheme('(r2l "' + sentence + '")')
    if display:
        print scheme("(cog-outgoing-set (car (cog-get-atoms 'SetLink)))")


class RelExServer(object):
    """
    RelEx server daemon
    """
    def __init__(self):
        self.process = None

    def start(self):
        """
        Bootstraps the RelEx daemon so that it will run in the
         background with the socket API so that further commands can be issued by
         sending them to the socket API
        """
        self.stop()
        # Start the OpenCog CogServer daemon
        if USE_VAGRANT:
            self.process = Process(target=run_vagrant_command,
                                   args=(VAGRANT_ID_RELEX, RELEX_START))
            self.process.daemon = True
            self.process.start()
        else:
            assert "Currently only implemented for Vagrant"

        sleep(OPENCOG_INIT_DELAY)

    def stop(self):
        """
        Terminate the RelEx daemon
        """
        if USE_VAGRANT:
            self.process = Process(target=run_vagrant_command,
                                   args=(VAGRANT_ID_RELEX, RELEX_STOP))
            self.process.daemon = True
            self.process.start()
        else:
            assert "Currently only implemented for Vagrant"


class Server(object):
    """
    OpenCog server daemon
    """
    def __init__(self):
        self.process = None

    def start(self):
        """
        Bootstraps the OpenCog CogServer daemon so that it will run in the
         background with the REST API so that further commands can be issued by
         sending them to the REST API
        """
        self.stop()
        # Start the OpenCog CogServer daemon
        if USE_VAGRANT:
            self.process = Process(target=run_vagrant_command,
                                   args=(VAGRANT_ID, OPENCOG_COGSERVER_START))
            self.process.daemon = True
            self.process.start()

        else:
            os.chdir(OPENCOG_SUBFOLDER)
            Popen([OPENCOG_COGSERVER_START])

        sleep(OPENCOG_INIT_DELAY)

        # Start the OpenCog REST API
        if USE_VAGRANT:
            self.process = Process(target=run_vagrant_command,
                                   args=(VAGRANT_ID, OPENCOG_RESTAPI_START))
            self.process.daemon = True
            self.process.start()
        else:
            os.system(OPENCOG_RESTAPI_START)

        sleep(OPENCOG_INIT_DELAY)

    @staticmethod
    def stop():
        """
        Terminate the OpenCog CogServer daemon
        """
        if USE_VAGRANT:
            try:
                shell('shutdown')
                sleep(OPENCOG_INIT_DELAY)
            except ConnectionError:
                pass
        else:
            os.system(OPENCOG_COGSERVER_STOP)
            sleep(OPENCOG_INIT_DELAY)
