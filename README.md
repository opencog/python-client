OpenCog Python Client
=====================

Defines an interface to allow OpenCog experiments to be written as short Python scripts.

#### Functionality

- Control an OpenCog server on your local machine or on a Vagrant box
- Control a RelEx server on a Vagrant box (local machine functionality not yet added)
- Start and stop the OpenCog server
- Start and stop the RelEx server
- Interact with the RelEx and RelEx2Logic NLP pipelines with single Python commands
- Control the steps of each mind agent
- Capture the contents of the attentional focus at each step in Scheme format
- Capture the discrete dynamical evolution of the attentional focus
- Capture the discrete dynamical evolution of the STI of each atom in the attentional focus
- Store the captured data as a timeseries in a CSV file for plotting and analysis (using pandas, matplotlib, SciPy, etc.)
- Render the captured data as a sequence of graphical visualizations of the attentional focus

#### Requirements

- Requires the REST API to be configured as described [here](https://github.com/opencog/opencog/blob/master/opencog/python/README.md) and installation of the [requests library](http://docs.python-requests.org/en/latest/user/install/#install)

- For full functionality, you should also install [PyMongo](http://api.mongodb.org/python/current/installation.html), [MongoDB](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/) and [GraphViz](http://www.graphviz.org/Download..php)

#### Example usage

##### IPython Notebook examples
The recommended way to learn how to use **python-client** is with IPython Notebook. An example demonstration is provided that combines documentation, interactive code execution, and graphical visualizations.

###### Simple example
**A simple example can be viewed online [here](http://nbviewer.ipython.org/github/opencog/python-client/blob/master/example.ipynb).**

###### NLP demo
**An NLP demo can be viewed online [here](http://nbviewer.ipython.org/github/opencog/python-client/blob/master/opencog-nlp.ipynb).**

**Note that the online versions are not interactive, whereas on your own machine they will be interactive.**

To run the example on your machine, you will need to install [IPython Notebook](http://ipython.org/notebook.html) first.

Then, run ```ipython notebook``` from the command line in this folder, and then open the notebook named ```example.ipynb```

##### Additional examples
See the usage example in ```example.py```

Also see an example visualization of the attentional focus dynamics as a slideshow of PNG images rendered from DOT representations in ```graphics.py```

#### Vagrant (optional)

**Note: These instructions are optional and only apply if you are planning to use Vagrant.**

The Client API can be used with Vagrant. For example, you can run the OpenCog daemon inside a virtual machine, and then do all of your Python development in Mac OS.

To set up OpenCog in this manner, follow these instructions:
http://wiki.opencog.org/w/Building_OpenCog_in_a_Linux_Virtual_Machine_on_Mac_OS_X

Then, install the Python packages [python-vagrant](https://pypi.python.org/pypi/python-vagrant) and [fabric](http://www.fabfile.org/installing.html).

Then, to use the Client API with Vagrant, open the file ```configuration.py``` and set the parameter ```USE_VAGRANT``` to ```True``` and ```VAGRANT_ID``` to the ID of your VM (you can find this using the command ```vagrant global-status```)

#### OpenCog Python Client API Documentation

The client API has docstrings for each method that describe correct usage. A summary of the available methods is presented below.

##### Server

**Before performing operations with OpenCog, you need to have an instance of a Server object:**

```
import opencog
server = opencog.Server()
server.start()
```

###### start()
    Bootstraps the OpenCog CogServer daemon so that it will run in the background with the
    REST API so that further commands can be issued by sending them to the REST API

###### stop()
    Terminate the OpenCog CogServer daemon

##### Operations

**After you have started a Server, you can perform the following operations.**

###### create_point(timestep, atoms, scheme=None)
    Create a PointInTime dictionary from a JSON atom representation

    Represents a discrete point in time in a time series from an experiment
    with the ECAN attention allocation discrete dynamical system

    Each point in time contains:

    - a list of "atoms" which consists of a list of objects of type Atom
      (Refer to the definition of the Atom object)
    - an integer "timestep"
    - (optional) A Scheme representation of the point in time

###### shell(command)
    Send a command to the CogServer shell

###### scheme(command)
    Send a Scheme command to the Scheme interpreter

###### load_scheme_files(files)
    Loads a list of Scheme files into the cogserver

###### load_python_agent(path)
    Load an arbitrary Python MindAgent in the CogServer

    Parameters:
    path (required) Relative path to the agent, including the filename,
      without the file extension

    Example of 'path':
      ../opencog/python/pln/examples/tuffy/smokes/smokes_agent
    
###### start_python_agent(path, name)
    Start a Python MindAgent that has already been loaded

    Parameters:
    path (required) Relative path to the agent, including the filename,
      without the file extension

    Example of 'path':
      ../opencog/python/pln/examples/tuffy/smokes/smokes_agent

    name (required) Name of the agent

    Example of 'name':
      InferenceAgent

###### step_agent(name)
    Run a step of an arbitrary C++ agent in the CogServer

    Parameters:
    name (required) Name of the agent

    Example of 'name':
      SimpleImportanceDiffusionAgent

###### step_python_agent(path, name)
    Run a step of an arbitrary Python agent in the CogServer

    Parameters:
    path (required) Relative path to the agent, including the filename,
      without the file extension
    name (required) Name of the agent

    Example of 'path':
      ../opencog/python/pln/examples/tuffy/smokes/smokes_agent
    Example of 'name':
      InferenceAgent

###### get_attentional_focus(timestep, scheme=False)
    Get the atoms in the attentional focus

    Parameters:
    timestep (required) You should provide a monotonically increasing timestep
      value to uniquely identify the timestep of this attentional focus
      snapshot.
    scheme (optional) If True, the Scheme representation of the attentional
      focus will also be captured. Default is False.

###### get_atomspace(timestep, scheme=False)
    Take a snapshot of the atomspace at a given point in time

    :param timestep: an integer representing a monotonically increasing
    timestep value which identifies the timestep of this atomspace snapshot
    :param scheme: If True, the Scheme representation of the atomspace will
    also be captured.
    :return: a PointInTime dictionary that captures the atomspace at the given
    timestep
    
###### atomspace()
    Retrieves a snapshot of the atomspace. Take note that the snapshot returned
    is static, and must be called again when you want it to be updated.
    
    :return: a dictionary of atoms

###### export_timeseries_csv(timeseries, filename, scheme=False)
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

###### export_timeseries_mongodb(timeseries)
    Export the timeseries to a MongoDB database.

    Parameters:
    timeseries (required) The timeseries that will be exported.
    
###### dump_atomspace_scheme()
    Returns all atoms in the atomspace in Scheme format
    
###### dump_atomspace_dot()
    Returns all atoms in the atomspace in DOT graph description language
    format
    
###### dump_attentional_focus_scheme()
    Returns all atoms in the attentional focus in Scheme format

###### clear_atomspace()
    Clear the atomspace

###### stop_agent_loop()
    Stop the automatic stepping of agents in the CogServer, so that agents
    can be stepped manually
    
###### set_af_boundary(value)
    Set the AttentionalFocusBoundary

    Parameters:
    value The STI value to set the AttentionalFocusBoundary to

###### importance_diffusion()
    Run a step of the simple importance diffusion agent

###### importance_updating()
    Run a step of the importance updating agent
    
###### hebbian_updating()
    Run a step of the hebbian updating agent

###### forgetting()
    Run a step of the forgetting agent

###### clear_mongodb()

###### set_diffusion_percent(value)
    Sets the diffusion percentage parameter for the importance diffusion agent
    value is a probability value between 0 and 1 representing the percentage
    of an atom's STI that should be diffused at each step

###### set_stimulus_amount(value)
    Sets the stimulus amount parameter for the PLN reasoning agent
    value is an Integer value representing the amount of stimulus to be assigned to the target

###### set_rent(value)
    Sets the rent parameter for the attention allocation importance updating agent
    value is an Integer value representing the amount of stimulus to be assigned to the target

###### set_wages(value)
    Sets the wages parameter for the attention allocation importance updating agent
    value is an Integer value representing the amount of stimulus to be assigned to the target

###### class Atom(object)
    Stores an atom handle and an STI value

    Represents the STI value of an atom at a particular point in time.
    Intended to be contained in a PointInTime object with a timestep value.

##### RelEx Server

**Before performing operations with RelEx, you need to have an instance of a RelExServer object:**

```
import opencog
relex_server = opencog.RelExServer()
relex_server.start()
```

**The following operations are available after starting a RelExServer:**

###### start()
    Bootstraps the RelEx server daemon so that it will run in the background with the
    socket API so that further commands can be issued by sending them to the socket API

###### stop()
    Terminate the RelEx server daemon

##### Operations

###### relex(sentence, display=True, concise=True)
    Interface to RelEx. Requires a RelExServer to be running.
    
    :param sentence: The sentence to send to RelEx for parsing
    :param display: Whether to print the output (default=True)
    :param concise: Whether to strip status messages from the output (default=True)
    :return: Human-readable parse of the sentence

###### to_logic(sentence, clear=True, display=True)
    Interface to Relex2Logic. Requires a Server and a RelExServer to be running.
    
    :param sentence: The sentence to send to RelEx2Logic for parsing
    :param clear: Whether to clear the atomspace before processing (default=True)
    :param display: Whether to print the output (default=True)
    :return: Contents of the SetLink representing the parsed sentence
