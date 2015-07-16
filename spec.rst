Overview
################

PVapp is an application designed to assist with measure and analysis of f silicon waffers. PVapp incorporate data collection from attached photoluminesce and photoconductance sensors, and transformation of these quantities into

This spec is not, by any stretch of the imagination, complete. Theses requirements will be refined over time with iterative feedback.



Measurement and UI components
#############################

=== Title
Standalone GUI interface
=== Description
Software should be opened in a machine which has the dependencies without crashing. User should be able to specify the location of the NI dll through gui or configuration file without touching the source code.
=== Estimate
Mostly done. 0.5 Day

=== Title
Save and load data
=== Description
- save experimental metadata, raw data and analysed data.
- load metadata, raw data, and processed data for continued analysis
- not necessary that data format should interoperable with labview
- data should be human readable (column headers, definition of parameters, (JSON?))
- load and saving files should update graph views, and program state
- user should be able to specify folder to save data
=== Estimate
Mostly done. 0.5 Day. Will need to update

=== Title
Graphics module for visualising data
=== Description
should be able to view experimental data
- zoom in and out
- move across field of vision (hand tool)
- set axises range
- set scale as linear or logarithmic
- change representation of graph (line graph or scatter plot)
=== Estimate
Mostly done. 0.5 day


=== Title
Panel for experimental wave form
=== Description
Panel to set experimental waveform to be sent to data card
These parameters are:
* period of the waveform : default: ???
* waveform shape (sine, square, triangle,  ) default: sine
* amplitude of waveform  default: ???
* wave form parameters (which vary with wave in question)
=== Estimate:
Mostly done. 0.5 day


=== Title
Set experimental parameters
=== Description
Have a panel in the GUI where the following experimental parameters are allowed to be modified
* initial offset (offset 1) default value: ???
* final offset (offset 2) default: ???
* number of repetitions of the experiment (repeats) default: 1
[NOTE: What is the expected behaviour for multiple measurements, should they be aggregated or processed individually?]
* sample rate (determine ) default: max sample rate
* invert channels
* set light source parameters (low intensity LED, high intensity LED, super high intensity flash)
all of these can be user set or sent to sensible defaults which are predetermined from NI card settings.
=== Estimate
mostly done. 0.5 day


=== Title
Data capture from NS card
=== Description
Transmit and receive Capture data from  NS card ensuring that measurement from all sensors happens syncronously
=== Estimate
Mostly done. 0.5 days


=== Title
Screen to dynamically determine offset
=== Description
Offers an interactive screen in which the user can manually set the offset for the observed data.
=== Estimate
1 day

=== Title
Automatic determination of gain for signal amplifier
=== Description
Program should be able to automatically detect clipping of signal measure, and change gain on signal amplifier to set optimal bound here.
[NOTE: how should this be done? My intuition is that if a certain proportion of values are are greater than a specified tolerance of the maximum value then this should be retried with smaller gain)
=== Estimate
2 days


=== Title
Have transformations available for raw data
=== Description
Allow all data (raw PL, PC, \Delta N) to be transformed with the following functions
* binning (parameters: bin width)
[NOTE: what is expected behaviour when # data points / bin width != 0 ]
* moving average (parameters: window size of MA)
* fourier transform (parameters: ???)
* truncate range (range of value outside of which series is truncated)
=== Estimate
Mostly done. 1 day.




Modelling components
#####################
N.B. in what follows a function of the form X(T) indicates the dependence of X on the temperature T


=== Title
PL model for estimation of excess carrier concentration \Delta n
=== Description
- panel to set model parameters for PL to \Delta n
- update graph with view of inferred \Delta n over time
--- Input
* A_i , scaling factor
* B(\delta N, T), radiative recombination coefficient
* N(T), ???
* N_het, ???
* A_i(T), temperature dependent scaling coefficent
[NOTE: how should these parameters be automatically determined?]
--- Model
\Delta n_PL is estimated with the formula
    \Delta n  = A_i * B(T) * \Delta n * (\Delta n + N)
--- Output
\Delta n
=== Estimate
3 days


=== Title
PC model for estimation of excess carrier concentration \Delta n
=== Description
- panel to set model parameters for photoconductance
- update graph with view of inferred \Delta n over time
--- Input
* comp, ???
* N_A, ???
* N_D, ???
* W, sample thickness
* n/p, ???
* diff (yes/no, 1 side, 5HR), ???
* bias, ???
* a, b, c, q, ???
* u_t(T), sum of electron and hole mobilities
[NOTE: how should these parameters be automatically determined?]
--- Model
[NOTE: I can't properly read the the details in the flow chart]
--- Output
* estimate of \delta n, excess carrier concentration
=== Estimate
3 Days


=== Title
Set model parameters for G, generation
=== Description
- panel to modify
--- Input
* V(G), ???
* R(T), ???
* fs, ???
* \alpha_si(T), ???
[NOTE: how should these parameters be automatically determined?]
--- Model
???
--- Output
G
=== Estimate
2 Days


=== Title
\Delta n model for minority carrier lifetime \tau
=== Description
- panel set model parameters for estimation of minority carrier lifetime \tau
- graph view where user can see effect of parameter changes on \tau
--- Input
* G, ???
* d\Delta n / dt, ???
* \Delta n, excess carrier concentration
--- Model
Minority carrier life time given by:
    \tau = \frac{\Delta n}{ G - d\Delta n / dt}
--- Output
\tau
=== Estimate
1 days

=== Title
Determine calibration constant A_i
=== Description
[NOTE: I am unclear what is require here]
=== Estimate
???

=== Title
Add temperature sensor to measurement system
==== Description
Allow temperature sensor data to be syncronously recorded along with the other sensor data.
=== Estimate
3 days

=== Title
Introduce temperature dependence in models
=== Description
Allow temperature dependent parameters in the PL, PC, G, and \tau models to be determined by appropriate functions instead of constant values.
=== Estimate
2 days


=== Title
Tutorial for setting up new model
=== Description
Write an in depth tutorial which will take beginner python user through steps of setting up an extension module for PVapp
=== Estimate
1 day
