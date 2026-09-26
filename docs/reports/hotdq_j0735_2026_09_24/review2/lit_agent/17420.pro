                                                  17420( 13) - 10-Sep-2024 15:52:25 - [  1]

                  HUBBLE SPACE TELESCOPE OBSERVING PROGRAM 17420

Version:  13  Check-in Time: 10-Sep-2024 15:52:25       STScI Edit Number: 2     

Title
A legacy survey for evolved planetary systems within 100pc                      
------------------------------------------------------------------------------------
Type             Cycle
SNAP             31       
------------------------------------------------------------------------------------
Investigators                                                                   
                                                                                     Contact?
    PI: Prof. Boris T. Gaensicke          University of Warwick                         Y 
   CoI: Dr. Nicola Gentile Fusillo        Universita degli Studi di Trieste             N 
   CoI: Prof. Detlev G. Koester           Universitat Kiel                              N 
   CoI: Dr. JJ Hermes                     Boston University                             N 
   CoI: Dr. Dimitri Veras                 University of Warwick                         N 
   CoI: Dr. Christopher James Manser      Imperial College of London                    N 
   CoI: Dr. Mark Hollands                 University of Sheffield                       N 
   CoI: Dr. Odette Fabiola Toloza         Universidad Tecnica Federico Santa Maria      N 
        Castillo                                                                          
   CoI: Dr. snehalata Sahu                University of Warwick                         N 
   CoI: Mr. Jamie Williams                University of Warwick                         N 

------------------------------------------------------------------------------------
Abstract

In just 25 years, we went from not knowing if the solar system is a fluke of Nature 
to realising that it is totally normal for stars to have planets. More remarkably,  
it is now clear that planet formation is a robust process, as rich multi-planet     
systems are found around stars more massive and less massive than the Sun. More     
recently, planetary systems have been identified in increasingly complex            
architectures, including circumbinary planets, wide binaries with planets orbiting  
one or both stellar components, and planets in triple stellar systems.              
                                                                                    
We have also learned that many planetary systems will survive the evolution of their
host stars into the white dwarf phase. Small bodies are scattered by unseen planets 
into the gravitational field of the white dwarfs, tidally disrupt, form dust discs, 
and eventually accrete onto the white dwarf, where they can be spectroscopically    
detected. HST/COS has played a critical role in the study these evolved planetary   
systems, demonstrating that overall the bulk composition of the debris is rocky and 
resembles in composition the inner the solar system, including evidence for         
water-rich planetesimals.                                                           
                                                                                    
Past observations of planetary systems at white dwarfs were limited to biased and   
incomplete samples. Here we propose a legacy HST survey of all white dwarfs within  
100pc identified with Gaia to answer the following questions:                       
                                                                                    
* How efficient is planet formation around 2-10Msun stars?                          
* What are the metallicities of the progenitors of debris-accreting white dwarfs?   
* What is the fate of circumbinary planets?                                         
* Can star-planet interactions generate magnetic fields in the white dwarf host?    
------------------------------------------------------------------------------------

  Observations Description
  ------------------------

                                                  17420( 13) - 10-Sep-2024 15:52:25 - [  2]

     ============================================================================   
     Original submission: 2023-Aug-30:                                              
     ============================================================================   
     This program is a continuation of our previous snapshot surveys of white dwarfs
     (12169, 12474, 13652, 14077, 15073, 16011, 16642). The overall goal of this    
     project is to identify white dwarfs that exhibit metal contamination,          
     indicating the accretion of debris from tidally disrupted asteroids. In this   
     Cycle 31 program, we focus on obtaining COS far-ultraviolet spectroscopy of    
     white dwarfs with temperatures in the range 15000-30000K, i.e. exploiting the  
     diagnostic potential of the strong resonance lines in the far-ultraviolet.     
                                                                                    
     The observations will be carried out with the G130M grating, which gives the   
     best coverage of all important lines (O I 1150A, C III 1175A, Si II 1260/65A, C
     II 1330/35A, Si IV 1393/1403). The 1291A central wavelength places the detector
     gap in a line-free region.                                                     
                                                                                    
     The targets for this program were chosen from the catalogue of Gentile Fusillo 
     et al. https://arxiv.org/abs/2106.07669 who identified white dwarfs based on   
     their Gaia astrometry and photometry, and determined their effective           
     temperatures (Teff) and surface gravities (log g) using the Gaia data.         
     Specifically, we selected white dwarfs with                                    
                                                                                    
     * d<=100pc                                                                     
     * 15000K < Teff < 30000K                                                       
                                                                                    
     We removed from that list all white dwarfs that have been previously observed  
     with COS/G130M, either in our snapshot programs, or other programs.            
                                                                                    
     Next, we computed white dwarf model spectra for all potential targets, using   
     the Teff and log g from the Gaia white dwarf catalogue, which in turn also     
     fixes the white dwarf radii - in other words, the model spectra are on an      
     absolute flux scale. We then computed synthetic magnitudes in the GALEX FUV    
     band, and selected the 150 FUV-brightest targets, excluding stars with FUV<12, 
     as these might violate the BOP. Finally, we carried out all ETC simulations for
     the target acquisition and G130M spectroscopy.                                 
                                                                                    
     To evaluate how good (and safe!) the synthetic magnitudes are, we cross-matched
     the 150 targets with the GALEX data base, and found 81 of them have been       
     observed by GALEX. Comparing the synthetic vs observed GALEX FUV magnitudes,   
     and we find that the synthetic magnitudes are brighter than the observed ones, 
     typically by ~0.2mag. Therefore, we conclude that the ETC simulations using the
     synthetic FUV magnitudes are on the conservative side.                         
                                                                                    
     The model spectra and a plot of the comparison of synthetic vs observed FUV    
     magnitudes are available here:                                                 
                                                                                    
     https://drive.google.com/drive/folders/1ZO_LLuutFLDvr2YsRPGBvBVtycVkJURD?usp=dr
     ive_link                                                                       
                                                                                    
     * the targets 1 - 36 are part of the ongoing snapshot survey #16642, and have  
     hance already undergone BOP screening.                                         
                                                                                    
     * the targets 137 - 250 are new targets. We used DA white dwarf models for the 
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [  3]

     appropriate temperature / surface gravity of each star to carry out the target 
     acquisition and spectroscopic ETC calculations. We broke the new targets up    
     into two groups:                                                               
                                                                                    
     1) The ten brightest new targets all have GALEX observations, to avoid any     
     slight uncertainty in the synthetic UV magnitudes bringing the objects too     
     close to the bright object limits, and we used the GALEX magnitudes to carry   
     out the ETC calculations.                                                      
     2) For the remaining 104 new targets, we used the synthetic UV magnitudes to   
     carry out the ETC calculations.                                                
                                                                                    
     ============================================================================   
     Update 2023-Nov-29:                                                            
     ============================================================================   
                                                                                    
     * Retired target #159 (WDJ040316.35+252016.80) and visit 59, as this target was
     observed as visit 0Y in program 16642 (my mistake was that this target should  
     have been in the "already BOP reviewed" set of targets, but this is moot by    
     now.                                                                           
                                                                                    
     * Retried target #22 (WDJ061634.64-043144.49) and visit 11, as this target was 
     observed as visit 74 in program 16642                                          
                                                                                    
     * Retired target #35 (WDJ045312.76-442340.14) and visit 07, as this target was 
     observed as visit 1S in program 16642                                          
                                                                                    
     * Retired target #8 (WDJ174435.13-725935.67) and visit 24, as this target was  
     observed as visit 16 in program 16642                                          
                                                                                    
     As before, targets in the range 1 to 36 are left-overs from the cycle 29       
     snapshot program 16642, and have passed their BOP checks back then. In more    
     detail: there are 30 targets left over from program 16642 that we re-use here, 
     and that have already passed their BOP checks. Details on the target and visit 
     ID in program 16642 and 17420 are summarised here:                             
     https://docs.google.com/spreadsheets/d/1lUcrOEyzAEoKw-FfnsldccKwCkoFW5m8UbgVIWS
     Gx8U/edit#gid=246676034                                                        
                                                                                    
     Ideally, these 30 targets could be implemented soon, while I sort out some     
     comments from John Debes regarding the new targets.                            
                                                                                    
     ============================================================================   
     Update 2023-Dec-14:                                                            
     ============================================================================   
                                                                                    
     (1) I carried out checks for visual companions within 9" of the targets using  
     Gaia DR3, and added notes on all cases in the target comment field. In most    
     cases, visual companions are distant and/or faint objects, however, I flagged a
     total of 18 bright nearby common proper motion companions, these are listed in 
                                                                                    
     https://docs.google.com/spreadsheets/d/1VJyGiZvhPd6IzTapTP4f3fmcNxTQ9ngohbc01tt
     tWQw/edit#gid=228866000                                                        
                                                                                    
     I placed all visits on hold that have (a) a red companion without Gaia Teff, or
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [  4]

     (b) a Gaia Teff<4300K. These are the following visit / target IDs:             
                                                                                    
     Visit Target                                                                   
     09 07 = WDJ052436.27-053510.52                                                 
     02 12 = WDJ014808.16-253243.36                                                 
     47 147 = WDJ123156.66-503247.99                                                
     50 150 = WDJ124428.57-011857.85                                                
     53 157 = WDJ114333.76-301312.83                                                
     54 154 = WDJ193708.15-513407.07                                                
     58 158 = WDJ185728.62+403534.87                                                
     91 191 = WDJ111658.44-163754.10                                                
     0B 201 = WDJ193845.80+264751.85                                                
     1R 234 = WDJ234100.34-540708.91                                                
                                                                                    
     (2) I added four new targets as replacement for the four targets retired in the
     update from 2023-Nov-29:                                                       
                                                                                    
     Visit Target                                                                   
     1Z 251 = WDJ211146.39+012054.26                                                
     2A 252 = WDJ085708.32-603245.24                                                
     2B 253 = WDJ031743.17+090955.15                                                
     2C 254 = WDJ074735.98+210635.83                                                
                                                                                    
     (3) John raised some concerns regarding the brightest targets because of GALEX 
     non-linearity effects. To clarify, I did all the ETC simulations with the      
     "non-scaled synthetic models", i.e. I did not use the observed GALEX           
     magnitudes. However, I realised that I copied and pasted the wrong BUFFER-TIMES
     a few of the brightest targets from my spreadsheet. I checked and replaced     
     where necessary the BUFFER-TIMES for the brightest targets, i.e. visits 37 to  
     55.                                                                            
                                                                                    
     For visits 37 to 2C I used the following:                                      
                                                                                    
     * for each target, I ran an ETC simulation with the "non-scaled synthetic      
     spectrum", and record the BUFFER-TIME from the ETC in the column "buffer", and 
     2/3 of that in "buffer 2/3".                                                   
     * sci_exp is the initial goal for the exposure time.                           
     * overheads can be minimsed as per                                             
     https://hst-docs.stsci.edu/cosihb/chapter-5-spectroscopy-with-cos/5-4-estimatin
     g-the-buffer-time-in-time-tag-mode                                             
     * I compute sci_exp-110, (sci_exp-110)/2, and (sci_exp-110)/3 in columns       
     "buffer n=1", "buffer n=2", "buffer n=3"                                       
     * if "buffer 2/3" > "buffer n=2", I set BUFFER-TIME = "buffer n=2" ("buffer    
     n=3" for visit 19)                                                             
     * if "buffer 2/3" < "buffer n=2", I set BUFFER-TIME = "buffer 2/3", and I      
     compute a new exposure time to be 3 x BUFFER-TIME + 110                        
                                                                                    
     Visits 1 to 36 were done with a similar, but slightly different approach as    
     part of program 16642, and were copied over from that program without changes. 
                                                                                    
     Full details are in this spreadsheet:                                          
     https://docs.google.com/spreadsheets/d/1VJyGiZvhPd6IzTapTP4f3fmcNxTQ9ngohbc01tt
     tWQw/edit#gid=89536053                                                         
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [  5]

                                                                                    
     The choice of exposure time and BUFFER-TIME are highlighted in green.          
                                                                                    
                                                                                    
     ============================================================================   
     Update 2024-Feb-14:                                                            
     ============================================================================   
                                                                                    
     Two visits executed so far failed because of guide star acquisition problems:  
     1C and 1F. We substituted the targets of two of the visits of white dwarfs with
     close red companions that are currently on hold with those of the two failed   
     visits to give them a second chance to be successfully observed, as the primary
     goal of this project is studying the occurence rate of planetary systems around
     single white dwarfs.                                                           
                                                                                    
     Visit 2 is now a repeat of the failed Visit 1C.                                
     Visit 53 is now a repeat of the failed Visit 1F.                               
                                                                                    
     Both repeat targets (WDJ162044.87-190133.35 and WDJ213712.53+473459.98) and    
     implementation should be straight-forward. These two repeat visits should not  
     count as duplications, as the initial observations did result in any data (the 
     shutter remained closed throughout the failed observations).                   
                                                                                    
     The original targets of Visits 2 and 53 (WDJ014808.16-253243.36 and            
     WDJ114333.76-301312.83) were withdrawn from the proposal.                      
                                                                                    
                                                                                    
     ============================================================================   
     Update 2024-Apr-04:                                                            
     ============================================================================   
     (1) Two of the on hold Visits of white dwarf + M-dwarfs were used to repeat    
     executed but failed Visits.                                                    
                                                                                    
     The Visits that failed were Visit 78 (WDJ085628.48+653946.01) failed because of
     guide star acquisition problems, and Visit 1B (WDJ040607.08+543132.1) had the  
     COS shutter closed during the first exposure ( lfac1byqq). We substituted these
     two targets into Visits 09 and 58 (which were on hold Visits). These repeat    
     visits should not count as duplication, as the initial observations did result 
     in any data (the shutter remained closed throughout the failed observations).  
     So in summary:                                                                 
                                                                                    
     Visit 58 is now a repeat of the failed Visit 78.                               
     Visit 09 is now a repeat of the failed Visit 1B.                               
                                                                                    
     Both targets (WDJ085628.48+653946.01 and WDJ040607.08+543132.1) were already   
     BOP screened (and observed / failed due to some observatory issues), so the    
     implementation should be straight-forward.                                     
                                                                                    
     The original targets of Visit 09 (WDJ052436.27-053510.52) and 58               
     (WDJ185728.62+403534.87) were withdrawn from the proposal.                     
                                                                                    
     (2) We keep six white dwarfs with cool nearby companions as backup orbits for  
     future failures of the (scientifically higher priority) single white dwarfs:   
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [  6]

                                                                                    
     Visit Target                                                                   
     57 147 = WDJ123156.66-503247.99                                                
     50 150 = WDJ124428.57-011857.85                                                
     54 154 = WDJ193708.15-513407.07                                                
     91 191 = WDJ111658.44-163754.10                                                
     0B 201 = WDJ193845.80+264751.85                                                
     1R 234 = WDJ234100.34-540708.91                                                
                                                                                    
     All other white dwarfs with close (hotter) main-sequence or white dwarfs have  
     been BOP cleared (some already observed) => nothing more to be done for the    
     visits in the Visual companions tab:                                           
                                                                                    
     https://docs.google.com/spreadsheets/d/1VJyGiZvhPd6IzTapTP4f3fmcNxTQ9ngohbc01tt
     tWQw/edit#gid=228866000                                                        
                                                                                    
                                                                                    
     (3) John raised some concerns regarding the brightest targets because of GALEX 
     non-linearity effects - and I think that following his concern, I actually     
     updated the Phase 2 using the wrong (scaling to GALEX magnitudes) strategy for 
     the new targets.                                                               
                                                                                    
     Hence I revisited all visits that are currently set to Implementation, and they
     fall into two sets:                                                            
                                                                                    
     Visits 12 and 17-36: their ETC simulations have all been done with the correct 
     procedure, i.e. scaling the WD model to the Teff, log g, and distance from the 
     Gaia white dwarf catalogue. These should all satisfy the BOP screening.        
                                                                                    
     https://docs.google.com/spreadsheets/d/1VJyGiZvhPd6IzTapTP4f3fmcNxTQ9ngohbc01tt
     tWQw/edit#gid=1615393836                                                       
                                                                                    
     Visits 37, 39-45, 52, 57: their ETC simulations were done with the wrong       
     procedure (i.e. scaling the WD model the the GALEX FUV magnitude). I re-ran    
     those with the correct procedure (scaling the models to the Gaia Teff, log g,  
     and distance). With the new results, Visits 37, 39-44 are too bright for       
     TIME-TAG, and I switched those to ACCUM mode. Visit 45 is fine.                
                                                                                    
     https://docs.google.com/spreadsheets/d/1VJyGiZvhPd6IzTapTP4f3fmcNxTQ9ngohbc01tt
     tWQw/edit#gid=89536053                                                         
                                                                                    
     (4) Visit 52: I re-ran the ETC simulation with the correct target model.       
                                                                                    
                                                                                    
     ============================================================================   
     Update 2024-Jun-16                                                             
     ============================================================================   
     The COS team became aware that the detectore is "used up" too quickly, hence   
     requested to reduce the exposure times where possible. I reviewed the exposure 
     times of the brightest targets with the goal of S/N=40 (using a list sent by   
     John) and the changes / no changes are recorded below:                         
                                                                                    
                                                                                    
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [  7]

     01 (WDJ013139.22-201958.63): https://etc.stsci.edu/etc/results/COS.sp.1925915/ 
     => S/N=40 requires 2689s => keep exposure time = 2 x 900s                      
     06 (WDJ045312.76-442340.14): https://etc.stsci.edu/etc/results/COS.sp.1925916/ 
     => S/N=40 requires 2763s => keep exposure time = 2 x 900s                      
     08 (WDJ050940.99+015308.63): https://etc.stsci.edu/etc/results/COS.sp.1925917/ 
     => S/N=40 requires 1913s => keep exposure time = 2 x 900s                      
     10 (WDJ053343.43-271350.08): https://etc.stsci.edu/etc/results/COS.sp.1925918/ 
     => S/N=40 requires 2312s => keep exposure time = 2 x 900s                      
     12 (WDJ085047.51+172602.06): https://etc.stsci.edu/etc/results/COS.sp.1925892/ 
     => S/N=40 requires 1628s => new exposure time = 2 x 800s                       
     13 (WDJ100551.52-023417.93): https://etc.stsci.edu/etc/results/COS.sp.1925919/ 
     => S/N=40 requires 2735s => keep exposure time = 2 x 900s                      
     14 (WDJ101511.71-010416.24): https://etc.stsci.edu/etc/results/COS.sp.1925920/ 
     => S/N=40 requires 2352s => keep exposure time = 2 x 900s                      
     15 (WDJ102846.64-214106.70): https://etc.stsci.edu/etc/results/COS.sp.1925921/ 
     => S/N=40 requires 2494s => keep exposure time = 2 x 900s                      
     17 (WDJ120347.43-002310.94): https://etc.stsci.edu/etc/results/COS.sp.1925922/ 
     => S/N=40 requires 2292s => keep exposure time = 2 x 900s                      
     18 (WDJ133913.54+120831.23): https://etc.stsci.edu/etc/results/COS.sp.1925923/ 
     => S/N=40 requires 3211s => keep exposure time = 2 x 900s                      
     19 (WDJ133915.05-370620.16): https://etc.stsci.edu/etc/results/COS.sp.1925924/ 
     => S/N=40 requires 1940s => keep exposure time = 2 x 900s                      
     21 (WDJ153037.04-355504.21): https://etc.stsci.edu/etc/results/COS.sp.1925893/ 
     => S/N=40 requires 945s => new exposure time = 2 x 450s                        
     22 (WDJ161523.98-111830.09): https://etc.stsci.edu/etc/results/COS.sp.1925925/ 
     => S/N=40 requires 2666s => keep exposure time = 2 x 900s                      
     23 (WDJ170256.34-531436.57): https://etc.stsci.edu/etc/results/COS.sp.1925926/ 
     => S/N=40 requires 1588s => new exposure time = 2 x 900s                       
     25 (WDJ181854.22-475748.50): https://etc.stsci.edu/etc/results/COS.sp.1925894/ 
     => S/N=40 requires 826s => new exposure time = 2 x 410s                        
     26 (WDJ184816.39-141522.33): https://etc.stsci.edu/etc/results/COS.sp.1925895/ 
     => S/N=40 requires 1722s => new exposure time = 2 x 860s                       
     27 (WDJ194925.91-440512.18): https://etc.stsci.edu/etc/results/COS.sp.1925896/ 
     => S/N=40 requires 781s => new exposure time = 2 x 390s                        
     28 (WDJ203210.13+215410.33): https://etc.stsci.edu/etc/results/COS.sp.1925897/ 
     => S/N=40 requires 872s => new exposure time = 2 x 435s                        
     29 (WDJ215453.40-302918.67): https://etc.stsci.edu/etc/results/COS.sp.1925898/ 
     => S/N=40 requires 650s => new exposure time = 2 x 325s                        
     31 (WDJ225510.55-631031.04): https://etc.stsci.edu/etc/results/COS.sp.1925899/ 
     => S/N=40 requires 1015s => new exposure time = 2 x 500s                       
     34 (WDJ234331.84-882310.21): https://etc.stsci.edu/etc/results/COS.sp.1925900/ 
     => S/N=40 requires 1029s => new exposure time = 2 x 515s                       
     36 (WDJ160317.23-192354.77): https://etc.stsci.edu/etc/results/COS.sp.1925901/ 
     => S/N=40 requires 1549 => new exposure time = 2 x 750s                        
     37 (WDJ023016.63+051550.70): https://etc.stsci.edu/etc/results/COS.sp.1925910/ 
     => S/N=40 requires 304s => new exposure time = 2 x 152s                        
     41 (WDJ012923.99+510846.97): https://etc.stsci.edu/etc/results/COS.sp.1925902/ 
     => S/N=40 requires 372s => new exposure time = 2 x 190s                        
     42 (WDJ164718.39+322832.87): https://etc.stsci.edu/etc/results/COS.sp.1925903/ 
     => S/N=40 requires 431s => new exposure time = 2 x 215s                        
     44 (WDJ042839.41+165812.09): https://etc.stsci.edu/etc/results/COS.sp.1925906/ 
     => S/N=40 requires 480s => new exposure time = 2 x 240s                        
     45 (WDJ213849.48-404127.74): https://etc.stsci.edu/etc/results/COS.sp.1925927/ 
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [  8]

     => S/N=40 requires 571s => new exposure time = 2 x 285s                        
     47 (WDJ123156.66-503247.99): https://etc.stsci.edu/etc/results/COS.sp.1925905/ 
     => S/N=40 requires 654s => new exposure time = 2 x 325s                        
     48 (WDJ020847.22+251409.97): https://etc.stsci.edu/etc/results/COS.sp.1925908/ 
     => S/N=40 requires 690s => new exposure time = 2 x 345s                        
     49 (WDJ002702.78-075111.86): https://etc.stsci.edu/etc/results/COS.sp.1925928/ 
     => S/N=40 requires 645s => new exposure time = 2 x 322s                        
     50 (WDJ124428.57-011857.85): https://etc.stsci.edu/etc/results/COS.sp.1925929/ 
     => S/N=40 requires 667s => new exposure time = 2 x 333s                        
     54 (WDJ193708.15-513407.07): https://etc.stsci.edu/etc/results/COS.sp.1925930/ 
     => S/N=40 requires 1498s => new exposure time = 2 x 749s                       
                                                                                    
                                                                                    
     ============================================================================   
     Update 2024-July-13                                                            
     ============================================================================   
                                                                                    
     * Following further discussions within the COS team, it was decided that the   
     maximum S/N of these snapshots @ 1310A should be 30.                           
     As requested by John, the following visits had their ETC simulations and       
     exposure & buffer times adjusted accordingly:                                  
                                                                                    
     01, 02, 06, 08, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29,
     34, 36, 37, 41, 42, 44, 45, 48, 49, 55, 56                                     
                                                                                    
     * I used three of the "on hold" visits (nearby red companions) to repeat failed
     snapshots, please check and activate:                                          
                                                                                    
     47 (WDJ221153.92+564946.77) is now a re-implementation of the failed visit 30  
     (WDJ221153.92+564946.77), but updated for S/N=30.                              
     50 (WDJ184225.24-780505.16) is now a re-implementation of the failed visit 0O  
     (WDJ184225.24-780505.16), but updated for S/N=30.                              
     54 (WDJ235200.03-033654.01) is now a re-implementation of the failed visit 1S  
     (WDJ235200.03-033654.01), but updated for S/N=30.                              
                                                                                    
     Visits remaining on hold because of nearby red companions are: 54, 91, 0B, 1R  
     => these remain "spares" to re-observed failed snaphots.                       
                                                                                    
     * Please check & activate the following visits:                                
                                                                                    
     09 (WDJ040607.08+543132.19): this visit is currently "inactive", it is a       
     re-implementation of the failed visit 1B (WDJ040607.08+543132.19), which had   
     the shutter closed during one exposure. 1B had been BOP screened.              
     12 (WDJ085047.51+172602.06): this visit is currently stuck as "implementation",
     I updated it for S/N=30, please check & activate                               
     48 (WDJ020847.22+251409.97): this visit is currently stuck as "implementation",
     I updated it for S/N=30, please check & activate                               
     57 (WDJ034306.45+320139.89): this visit is currently stuck as "implementation",
     I updated it for S/N=30, please check & activate                               
     58 (WDJ085628.48+653946.01): this visit is currently "inactive", it is a       
     re-implementation of the failed visit 78 (WDJ085628.48+653946.01), which had   
     the shutter closed during one exposure. 78 had been BOP screened.              
                                                                                    
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [  9]

                                                                                    
                                                                                    
     ============================================================================   
     Update 2024-Sep-09                                                             
     ============================================================================   
                                                                                    
                                                                                    
     * I used two of the "on hold" visits (nearby red companions) to repeat failed  
     snapshots, please check and activate. Both targets have been BOP cleared       
     before.                                                                        
                                                                                    
     0B (WDJ234331.84-882310.21) is now a re-implementation of the failed visit 34  
     (WDJ234331.84-882310.21).                                                      
     1R (WDJ235200.03-033654.01) is now a re-implementation of the failed visit 54  
     (WDJ235200.03-033654.01).                                                      
------------------------------------------------------------------------------------

                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 10]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
1   WDJ215453.40 STAR, DA                RA=21H54M53.4337S +/- 0.05",     J2000             V = 14.702 +/- 0.003                    
    -302918.67                           DEC=-30D29'18.88" +/- 0.05"                        SYNTHETIC_FUV=13.01                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.002029250472356872                     -0.013519999999999999            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
2   WDJ031715.85 STAR, DA                RA=03H17M14.8342S +/- 0.05",     J2000             V = 14.754 +/- 0.004                    
    -853225.56                           DEC=-85D32'25.75" +/- 0.05"                        SYNTHETIC_FUV=13.16                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              CPM WD at 7.1" (Gaia DR3 4613612951211823616) - which is    
              also a target of this snapshot survey (target #14).         

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.06329311571654775                     -0.01201                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
3   WDJ194925.91 STAR, DA                RA=19H49M25.9935S +/- 0.05",     J2000             V = 14.788 +/- 0.003 GALEX_FUV=13.63    
    -440512.18                           DEC=-44D05'12.83" +/- 0.05"                        SYNTHETIC_FUV=13.20                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.005011007057135403                     -0.040659999999999995            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
4   WDJ181854.22 STAR, DA                RA=18H18M54.2673S +/- 0.05",     J2000             V = 14.708 +/- 0.003                    
    -475748.50                           DEC=-47D57'48.33" +/- 0.05"                        SYNTHETIC_FUV=13.24                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              Crowded target area, three faint (20th mag) background      
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.003182971722496675                     0.01046                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 11]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
5   WDJ203210.13 STAR, DA                RA=20H32M10.1361S +/- 0.05",     J2000             V = 14.743 +/- 0.003                    
    +215410.33                           DEC=+21D54'11.41" +/- 0.05"                        SYNTHETIC_FUV=13.30                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              Crowded target area, two faint (19-20th mag) background     
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               4.771062883706406E-4                     0.06741                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
6   WDJ040223.78 STAR, DA                RA=04H02M23.7244S +/- 0.05",     J2000             V = 14.895 +/- 0.003                    
    +320153.80                           DEC=+32D01'54.37" +/- 0.05"                        SYNTHETIC_FUV=13.31                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0035474121654641227                   0.03501                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
9   WDJ225510.55 STAR, DA                RA=22H55M10.8049S +/- 0.05",     J2000             V = 14.144 +/- 0.003                    
    -631031.04                           DEC=-63D10'32.52" +/- 0.05"                        SYNTHETIC_FUV=13.32                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.016157862448993525                     -0.09262999999999999             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
10  WDJ153037.04 STAR, DA                RA=15H30M37.0191S +/- 0.05",     J2000             V = 14.323 +/- 0.003                    
    -355504.21                           DEC=-35D55'5.23" +/- 0.05"                         SYNTHETIC_FUV=13.35                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              Crowded target area, five faint (18-20th mag) background    
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.001445524180499155                    -0.06405                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 12]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
11  WDJ170256.34 STAR, DA                RA=17H02M56.3335S +/- 0.05",     J2000             V = 13.526 +/- 0.003                    
    -531436.57                           DEC=-53D14'38.92" +/- 0.05"                        SYNTHETIC_FUV=13.36                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              Crowded target area, seven faint (18-21th mag) background   
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -2.584642223246986E-4                    -0.14702                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
13  WDJ234331.84 STAR, DA                RA=23H43M31.2420S +/- 0.05",     J2000             V = 14.943 +/- 0.003 GALEX_FUV=13.71    
    -882310.21                           DEC=-88D23'10.05" +/- 0.05"                        SYNTHETIC_FUV=13.48                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.03766076078057675                     0.009859999999999999             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
14  WDJ031719.13 STAR, DA                RA=03H17M18.2806S +/- 0.05",     J2000             V = 14.079 +/- 0.003                    
    -853231.29                           DEC=-85D32'31.65" +/- 0.05"                        SYNTHETIC_FUV=13.59                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              CPM WD at 7.1" (Gaia DR3 4613612951211823104) - which is    
              also a target of this snapshot survey (target #2).          

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.05298090195223257                     -0.02237                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
15  WDJ221153.92 STAR, DA                RA=22H11M54.3740S +/- 0.05",     J2000             V = 14.126 +/- 0.003                    
    +564946.77                           DEC=+56D49'48.83" +/- 0.05"                        SYNTHETIC_FUV=13.60                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              Distant background object at 6.6": Gaia DR3                 
              2198430794895636352, plx=0.4mas, Bp=15.43, Rp=14.24. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.02853478739020123                      0.12894999999999998              0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 13]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
16  WDJ104346.70 STAR, DA                RA=10H43M46.5639S +/- 0.05",     J2000             V = 15.165 +/- 0.003                    
    -390637.35                           DEC=-39D06'36.76" +/- 0.05"                        SYNTHETIC_FUV=13.65                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.008407931631996336                    0.03735                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
17  WDJ232337.94 STAR, DA                RA=23H23M37.8895S +/- 0.05",     J2000             V = 14.793 +/- 0.003 GALEX_FUV=14.04    
    +341526.71                           DEC=+34D15'26.40" +/- 0.05"                        SYNTHETIC_FUV=13.77                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0031078180663988934                   -0.01975                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
18  WDJ234805.65 STAR, DA                RA=23H48M5.6595S +/- 0.05",      J2000             V = 14.662 +/- 0.003 GALEX_FUV=14.05    
    +410215.96                           DEC=+41D02'16.54" +/- 0.05"                        SYNTHETIC_FUV=13.80                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               8.007688154394856E-4                     0.03646                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
19  WDJ085047.51 STAR, DA                RA=08H50M47.4255S +/- 0.05",     J2000             V = 14.698 +/- 0.003 GALEX_FUV=14.21    
    +172602.06                           DEC=+17D26'1.55" +/- 0.05"                         SYNTHETIC_FUV=13.83                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.005153393243883261                    -0.03175                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 14]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
20  WDJ184816.39 STAR, DA                RA=18H48M16.3549S +/- 0.05",     J2000             V = 14.997 +/- 0.003                    
    -141522.33                           DEC=-14D15'22.63" +/- 0.05"                        SYNTHETIC_FUV=13.96                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              This target was observed before with the same setup, but    
              the guide star acqusition failed, and the target drifted    
              out of the aperture (flux lost). The exposure ID is         
              LEQC67010.                                                  
              Crowded target area, eleven faint (18-20th mag) background  
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.002005082045374146                    -0.018969999999999997            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
21  WDJ142234.18 STAR, DA                RA=14H22M34.2045S +/- 0.05",     J2000             V = 15.115 +/- 0.003 GALEX_FUV=14.12    
    -102408.81                           DEC=-10D24'8.78" +/- 0.05"                         SYNTHETIC_FUV=13.99                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0014484740971490962                    0.0062900000000000005            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
23  WDJ050940.99 STAR, DA                RA=05H09M41.0323S +/- 0.05",     J2000             V = 15.063 +/- 0.003 GALEX_FUV=14.55    
    +015308.63                           DEC=+01D53'8.40" +/- 0.05"                         SYNTHETIC_FUV=14.05                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0025433772924811386                    -0.01434                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
24  WDJ133915.05 STAR, DA                RA=13H39M14.9838S +/- 0.05",     J2000             V = 15.503 +/- 0.003 GALEX_FUV=14.29    
    -370620.16                           DEC=-37D06'20.54" +/- 0.05"                        SYNTHETIC_FUV=14.14                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              Distant background object at 6.1": Gaia DR3                 
              2198430794895636352, plx=0.22mas, Bp=20.2, Rp=18.5. Not an  
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.004447933817015501                    -0.02293                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 15]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
25  WDJ120347.43 STAR, DA                RA=12H03M47.3133S +/- 0.05",     J2000             V = 15.175 +/- 0.003 GALEX_FUV=14.51    
    -002310.94                           DEC=-00D23'11.38" +/- 0.05"                        SYNTHETIC_FUV=14.21                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.006991492400114875                    -0.02788                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
26  WDJ053343.43 STAR, DA                RA=05H33M43.3844S +/- 0.05",     J2000             V = 15.614 +/- 0.003 GALEX_FUV=14.43    
    -271350.08                           DEC=-27D13'50.96" +/- 0.05"                        SYNTHETIC_FUV=14.26                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              Distant background object at 7.6": Gaia DR3                 
              2908425653827914752, plx=3.3mas, G=19.8. Not an M-dwarf, no 
              concern for BOP.                                            

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0030560323294972795                   -0.05527                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
27  WDJ043659.47 STAR, DA                RA=04H36M59.5013S +/- 0.05",     J2000             V = 15.746 +/- 0.003                    
    +253547.49                           DEC=+25D35'46.77" +/- 0.05"                        SYNTHETIC_FUV=14.32                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.002259773645739231                     -0.045020000000000004            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
28  WDJ101511.71 STAR, DA                RA=10H15M11.7179S +/- 0.05",     J2000             V = 15.565 +/- 0.003 GALEX_FUV=14.34    
    -010416.24                           DEC=-01D04'16.14" +/- 0.05"                        SYNTHETIC_FUV=14.33                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               3.440601238823152E-4                     0.00579                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 16]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
29  WDJ133913.54 STAR, DA                RA=13H39M13.6684S +/- 0.05",     J2000             V = 14.701 +/- 0.003                    
    +120831.23                           DEC=+12D08'29.10" +/- 0.05"                        SYNTHETIC_FUV=14.34                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              Distant background object at 7.6": Gaia DR3                 
              3738752641572841472, plx=-0.6mas, Bp=20.0, Rp=19.3. Not an  
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.00832215446988093                      -0.13306                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
30  WDJ102846.64 STAR, DA                RA=10H28M46.3326S +/- 0.05",     J2000             V = 15.36 +/- 0.003 GALEX_FUV=14.50     
    -214106.70                           DEC=-21D41'6.85" +/- 0.05"                         SYNTHETIC_FUV=14.36                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.019456298028285305                    -0.00937                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
31  WDJ013139.22 STAR, DA                RA=01H31M39.4133S +/- 0.05",     J2000             V = 15.325 +/- 0.003 GALEX_FUV=14.49    
    -201958.63                           DEC=-20D19'58.43" +/- 0.05"                        SYNTHETIC_FUV=14.41                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.011858935212821343                     0.012539999999999999             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
32  WDJ100551.52 STAR, DA                RA=10H05M51.3994S +/- 0.05",     J2000             V = 15.297 +/- 0.003 GALEX_FUV=14.59    
    -023417.93                           DEC=-02D34'17.19" +/- 0.05"                        SYNTHETIC_FUV=14.42                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.007418136312387072                    0.046549999999999994             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
33  WDJ233738.74 STAR, DA                RA=23H37M38.9112S +/- 0.05",     J2000             V = 15.141 +/- 0.003                    
    -411032.64                           DEC=-41D10'34.72" +/- 0.05"                        SYNTHETIC_FUV=14.42                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.011007671663424885                     -0.12984                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 17]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
34  WDJ161523.98 STAR, DA                RA=16H15M24.0139S +/- 0.05",     J2000             V = 15.459 +/- 0.003                    
    -111830.09                           DEC=-11D18'31.64" +/- 0.05"                        SYNTHETIC_FUV=14.42                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.002340780547759258                     -0.09688                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
36  WDJ160317.23 STAR, DA                RA=16H03M17.2399S +/- 0.05",     J2000             V = 15.059 +/- 0.003                    
    -192354.77                           DEC=-19D23'54.67" +/- 0.05"                        SYNTHETIC_FUV=13.87                     
    Reference Frame: ICRS    Extended: NO
    Comments: This target is part of the Cycle 29 snapshot survey         
              (id=16642) and has been screened for BOP.                   
              This target was observed before with the same setup, but    
              the guide star acqusition failed, and the target drifted    
              out of the aperture (flux lost). The exposure ID is         
              LEQC62010.                                                  

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               5.131297385314927E-4                     0.0065                           0.0                     
------------------------------------------------------------------------------------------------------------------------------------
137 WDJ023016.63 STAR, DA                RA=02H30M16.7100S +/- 0.05",     J2000             V = 12.82 +/- 0.003 GALEX_FUV=12.53     
    +051550.70                           DEC=+05D15'50.30" +/- 0.05"                        SYNTHETIC_FUV=12.02                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0051523964645973416                    -0.0245                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
138 WDJ201056.85 STAR, DA                RA=20H10M56.4279S +/- 0.05",     J2000             V = 12.26 +/- 0.003 GALEX_FUV=12.58     
    -301306.63                           DEC=-30D13'10.62" +/- 0.05"                        SYNTHETIC_FUV=12.09                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.026298576716654                       -0.24941999999999998             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
139 WDJ215225.38 STAR, DA                RA=21H52M25.3953S +/- 0.05",     J2000             V = 12.78 +/- 0.003 GALEX_FUV=12.97     
    +022319.58                           DEC=+02D23'14.77" +/- 0.05"                        SYNTHETIC_FUV=12.17                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0010222206324726176                    -0.30052999999999996             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
140 WDJ014128.80 STAR, DA                RA=01H41M27.6542S +/- 0.05",     J2000             V = 13.12 +/- 0.003 GALEX_FUV=13.00     
    +833458.83                           DEC=+83D35'0.19" +/- 0.05"                         SYNTHETIC_FUV=12.29                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.07168523727611882                     0.08492                          0.0                     
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 18]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------
141 WDJ012923.99 STAR, DA                RA=01H29M24.0505S +/- 0.05",     J2000             V = 13.54 +/- 0.003 GALEX_FUV=12.72     
    +510846.97                           DEC=+51D08'45.20" +/- 0.05"                        SYNTHETIC_FUV=12.33                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.003500496650390683                     -0.11073999999999999             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
142 WDJ164718.39 STAR, DA                RA=16H47M18.1915S +/- 0.05",     J2000             V = 13.58 +/- 0.003 GALEX_FUV=13.06     
    +322832.87                           DEC=+32D28'33.27" +/- 0.05"                        SYNTHETIC_FUV=12.48                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.01256177819453296                     0.02544                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
143 WDJ022827.20 STAR, DA                RA=02H28M27.1151S +/- 0.05",     J2000             V = 13.85 +/- 0.003 GALEX_FUV=13.25     
    -324233.80                           DEC=-32D42'37.28" +/- 0.05"                        SYNTHETIC_FUV=12.64                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.005536717366255556                    -0.21781                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
144 WDJ042839.41 STAR, DA                RA=04H28M39.5247S +/- 0.05",     J2000             V = 14.05 +/- 0.003 GALEX_FUV=12.93     
    +165812.09                           DEC=+16D58'11.66" +/- 0.05"                        SYNTHETIC_FUV=12.64                     
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 7.2": Gaia DR3                 
              3313714023601950080, plx=0.65mas, Bp=19.12, Rp=17.6. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0071437170257855195                    -0.02709                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
145 WDJ213849.48 STAR, DA                RA=21H38M49.2858S +/- 0.05",     J2000             V = 13.52 +/- 0.003 GALEX_FUV=12.87     
    -404127.74                           DEC=-40D41'26.93" +/- 0.05"                        SYNTHETIC_FUV=12.69                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.012131620993983913                    0.051                            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
146 WDJ005340.54 STAR, DA                RA=00H53M40.5176S +/- 0.05",     J2000             V = 14.38 +/- 0.003 GALEX_FUV=13.35     
    +360118.17                           DEC=+36D01'16.25" +/- 0.05"                        SYNTHETIC_FUV=12.74                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.001662546049429292                    -0.11976                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 19]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
148 WDJ020847.22 STAR, DA                RA=02H08M47.7129S +/- 0.05",     J2000             V = 13.23 +/- 0.003 SYNTHETIC_FUV=12.84 
    +251409.97                           DEC=+25D14'8.05" +/- 0.05"                                                                 
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.030878277296411495                     -0.12007999999999999             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
149 WDJ002702.78 STAR, DA                RA=00H27M2.7451S +/- 0.05",      J2000             V = 14.1 +/- 0.003 GALEX_FUV=13.20      
    -075111.86                           DEC=-07D51'11.51" +/- 0.05"                        SYNTHETIC_FUV=12.93                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0023143722239691443                   0.0219                           0.0                     
------------------------------------------------------------------------------------------------------------------------------------
151 WDJ041051.67 STAR, DA                RA=04H10M51.6520S +/- 0.05",     J2000             V = 14.72 +/- 0.003 GALEX_FUV=13.43     
    +592503.39                           DEC=+59D25'1.54" +/- 0.05"                         SYNTHETIC_FUV=12.99                     
    Reference Frame: ICRS    Extended: NO
    Comments: Crowded target area, two faint (18-20th mag) background     
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -9.145979364198596E-4                    -0.11572                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
152 WDJ213611.14 STAR, DA                RA=21H36M11.2681S +/- 0.05",     J2000             V = 14.39 +/- 0.003 SYNTHETIC_FUV=13.32 
    -260959.43                           DEC=-26D09'59.79" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 7.8": Gaia DR3                 
              6814117867400118016, plx=1.6mas, Bp=18.54, Rp=17.81. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.007836447550507993                     -0.0224                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
155 WDJ084041.95 STAR, DA                RA=08H40M41.4280S +/- 0.05",     J2000             V = 14.65 +/- 0.003 GALEX_FUV=15.73     
    +553958.80                           DEC=+55D39'52.90" +/- 0.05"                        SYNTHETIC_FUV=14.02                     
    Reference Frame: ICRS    Extended: NO
    Comments: G-type cpm at 5.4": Gaia DR3 1031072805679914880, Bp=7.30,  
              Rp=8.18, Gaia Teff=5584K.                                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.03277219897746295                     -0.3683                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 20]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
156 WDJ080710.46 STAR, DA                RA=08H07M10.4082S +/- 0.05",     J2000             V = 14.51 +/- 0.003 SYNTHETIC_FUV=14.07 
    -362251.69                           DEC=-36D22'50.04" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 7.0": Gaia DR3                 
              5544588997154160000, plx=0.45mas, Bp=16.75, Rp=15.24. Not   
              an M-dwarf, no concern for BOP.                             

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.003178092758574869                    0.10273                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
157 WDJ034306.45 STAR, DA                RA=03H43M6.5114S +/- 0.05",      J2000             V = 14.65 +/- 0.003 SYNTHETIC_FUV=14.22 
    +320139.89                           DEC=+32D01'38.81" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.003835050473427213                     -0.06777                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
160 WDJ080016.15 STAR, DA                RA=08H00M16.0508S +/- 0.05",     J2000             V = 15.92 +/- 0.003 GALEX_FUV=16.28     
    +004045.91                           DEC=+00D40'44.86" +/- 0.05"                        SYNTHETIC_FUV=14.46                     
    Reference Frame: ICRS    Extended: NO
    Comments: K-type cpm at 4": Gaia DR3 3084313528195320960, Bp=12.22,   
              Rp=10.81, Gaia Teff=4593K                                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.005912415324525579                    -0.06551                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
161 WDJ193505.26 STAR, DA                RA=19H35M5.2723S +/- 0.05",      J2000             V = 15.67 +/- 0.003 GALEX_FUV=14.65     
    -173953.55                           DEC=-17D39'53.29" +/- 0.05"                        SYNTHETIC_FUV=14.48                     
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 7.1": Gaia DR3                 
              4179983226127791104, plx=0.4mas, Bp=17.26, Rp=16.37. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               8.444858009841887E-4                     0.01682                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
162 WDJ093538.07 STAR, DA                RA=09H35M38.0066S +/- 0.05",     J2000             V = 15.52 +/- 0.003 SYNTHETIC_FUV=14.49 
    -585600.61                           DEC=-58D56'1.96" +/- 0.05"                                                                 
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0040437164814826725                   -0.08424                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
163 WDJ103349.20 STAR, DA                RA=10H33M49.1371S +/- 0.05",     J2000             V = 15.65 +/- 0.003 SYNTHETIC_FUV=14.49 
    +230916.26                           DEC=+23D09'16.07" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0037261481804633668                   -0.01182                         0.0                     
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 21]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------
164 WDJ154100.93 STAR, DA                RA=15H41M0.8783S +/- 0.05",      J2000             V = 15.54 +/- 0.003 SYNTHETIC_FUV=14.50 
    -362214.98                           DEC=-36D22'15.54" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.00297650752838491                     -0.03543                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
165 WDJ010419.33 STAR, DA                RA=01H04M19.2701S +/- 0.05",     J2000             V = 14.99 +/- 0.003 GALEX_FUV=14.81     
    +381655.23                           DEC=+38D16'54.58" +/- 0.05"                        SYNTHETIC_FUV=14.52                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0037462014983491027                   -0.040490000000000005            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
166 WDJ201719.80 STAR, DA                RA=20H17M19.7722S +/- 0.05",     J2000             V = 15.05 +/- 0.003 GALEX_FUV=14.66     
    -074819.01                           DEC=-07D48'19.53" +/- 0.05"                        SYNTHETIC_FUV=14.52                     
    Reference Frame: ICRS    Extended: NO
    Comments: Two distant background objects.                             
              At 6.0": Gaia DR3 4215838781340369408, plx=1.2mas,          
              Bp=17.26, Rp=16.37. Not an M-dwarf, no concern for BOP.     
              At 7.5": Gaia DR3 4215838781345197440, plx=0.4mas,          
              Bp=20.12, Rp=18.93. Not an M-dwarf, no concern for BOP.     

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0019292074676808845                   -0.03264                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
167 WDJ030350.56 STAR, DA                RA=03H03M50.8080S +/- 0.05",     J2000             V = 14.96 +/- 0.003 GALEX_FUV=17.51     
    +060748.75                           DEC=+06D07'49.62" +/- 0.05"                        SYNTHETIC_FUV=14.52                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.015273343219125012                     0.054                            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
168 WDJ191850.20 STAR, DA                RA=19H18M50.2456S +/- 0.05",     J2000             V = 15.38 +/- 0.003 SYNTHETIC_FUV=14.53 
    +333602.29                           DEC=+33D36'2.80" +/- 0.05"                                                                 
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background objects at 6.3": Gaia DR3                
              2049244315590314368, plx=-1.1mas, Bp=21.08, Rp=20.4. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0028550375852104686                    0.03251                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 22]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
169 WDJ052658.86 STAR, DA                RA=05H26M59.1074S +/- 0.05",     J2000             V = 15.46 +/- 0.003 SYNTHETIC_FUV=14.53 
    -702617.08                           DEC=-70D26'15.22" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Crowded target area, 14 faint (19-20th mag) background      
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.015342929914859622                     0.11581999999999999              0.0                     
------------------------------------------------------------------------------------------------------------------------------------
170 WDJ145333.03 STAR, DA                RA=14H53M32.9533S +/- 0.05",     J2000             V = 15.51 +/- 0.003 GALEX_FUV=14.65     
    -304023.77                           DEC=-30D40'23.88" +/- 0.05"                        SYNTHETIC_FUV=14.54                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0044972032962329                      -0.00741                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
171 WDJ073739.33 STAR, DA                RA=07H37M39.2301S +/- 0.05",     J2000             V = 14.72 +/- 0.003 SYNTHETIC_FUV=14.55 
    -294456.83                           DEC=-29D44'57.09" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 5.8": Gaia DR3                 
              5599365360779914240, plx=0.6mas, Bp=16.25, Rp=15.32. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.006469280174370902                    -0.01534                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
172 WDJ154754.64 STAR, DA                RA=15H47M54.7219S +/- 0.05",     J2000             V = 15.73 +/- 0.003 SYNTHETIC_FUV=14.55 
    -432801.53                           DEC=-43D28'2.20" +/- 0.05"                                                                 
    Reference Frame: ICRS    Extended: NO
    Comments: Two faint (19-20th mag) background objects within 9".       
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.004940977099022585                     -0.04246                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 23]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
173 WDJ192000.84 STAR, DA                RA=19H20M0.7777S +/- 0.05",      J2000             V = 15.55 +/- 0.003 GALEX_FUV=14.58     
    -224152.97                           DEC=-22D41'54.03" +/- 0.05"                        SYNTHETIC_FUV=14.55                     
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background objects at 5.0": Gaia DR3                
              6771076866261273344, plx=-0.2mas, Bp=20.31, Rp=19.04. Not   
              an M-dwarf, no concern for BOP.                             

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.004142868215232163                    -0.0664                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
174 WDJ043704.01 STAR, DA                RA=04H37M4.0294S +/- 0.05",      J2000             V = 15.63 +/- 0.003 SYNTHETIC_FUV=14.56 
    -572821.62                           DEC=-57D28'20.20" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               8.914386176199989E-4                     0.08886                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
175 WDJ205538.86 STAR, DA                RA=20H55M38.9445S +/- 0.05",     J2000             V = 14.98 +/- 0.003 GALEX_FUV=14.69     
    -174004.87                           DEC=-17D40'6.45" +/- 0.05"                         SYNTHETIC_FUV=14.56                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.005273420731095927                     -0.09859                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
176 WDJ080132.70 STAR, DA                RA=08H01M32.6292S +/- 0.05",     J2000             V = 15.19 +/- 0.003 GALEX_FUV=14.66     
    -060735.48                           DEC=-06D07'35.04" +/- 0.05"                        SYNTHETIC_FUV=14.57                     
    Reference Frame: ICRS    Extended: NO
    Comments: Two distant (17-20th mag) background objects within 9".     
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.00441722733475097                     0.027                            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
177 WDJ200946.56 STAR, DA                RA=20H09M46.4402S +/- 0.05",     J2000             V = 15.45 +/- 0.003 SYNTHETIC_FUV=14.58 
    -772116.06                           DEC=-77D21'17.53" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.00729060476498981                     -0.09158                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
178 WDJ085628.48 STAR, DA                RA=08H56M28.4532S +/- 0.05",     J2000             V = 15.43 +/- 0.003 GALEX_FUV=14.72     
    +653946.01                           DEC=+65D39'46.21" +/- 0.05"                        SYNTHETIC_FUV=14.58                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.001915367431360367                    0.01252                          0.0                     
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 24]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------
179 WDJ052137.30 STAR, DA                RA=05H21M37.2937S +/- 0.05",     J2000             V = 15.68 +/- 0.003 SYNTHETIC_FUV=14.58 
    -111434.43                           DEC=-11D14'34.84" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -6.46405115284887E-4                     -0.02582                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
180 WDJ222734.23 STAR, DA                RA=22H27M34.2401S +/- 0.05",     J2000             V = 15.32 +/- 0.003 GALEX_FUV=14.67     
    -601142.21                           DEC=-60D11'43.06" +/- 0.05"                        SYNTHETIC_FUV=14.59                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               6.77336082470381E-4                      -0.053270000000000005            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
181 WDJ122448.14 STAR, DA                RA=12H24M48.1667S +/- 0.05",     J2000             V = 15.54 +/- 0.003 GALEX_FUV=14.75     
    +792042.55                           DEC=+79D20'43.03" +/- 0.05"                        SYNTHETIC_FUV=14.59                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0019723448930464333                    0.03057                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
182 WDJ181348.56 STAR, DA                RA=18H13M48.5775S +/- 0.05",     J2000             V = 15.29 +/- 0.003 SYNTHETIC_FUV=14.59 
    +211920.66                           DEC=+21D19'21.24" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Two distant (17-20th mag) background objects within 9".     
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.001298197434782797                     0.03612                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
183 WDJ022340.37 STAR, DA                RA=02H23M40.5472S +/- 0.05",     J2000             V = 15.08 +/- 0.003 SYNTHETIC_FUV=14.60 
    +481647.23                           DEC=+48D16'46.86" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.011053425312373548                     -0.023309999999999997            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 25]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
184 WDJ150040.16 STAR, DA                RA=15H00M40.1170S +/- 0.05",     J2000             V = 15.02 +/- 0.003 SYNTHETIC_FUV=14.60 
    -370338.80                           DEC=-37D03'37.83" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 8.2": Gaia DR3                 
              6198878954897638528, plx=0.5mas, Bp=15.92, Rp=15.07. Not an 
              M-dwarf, no concern for BOP. Gaia Teff=5673K                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0026390993773041478                   0.06103                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
185 WDJ084215.02 STAR, DA                RA=08H42M14.9439S +/- 0.05",     J2000             V = 16.0 +/- 0.003 SYNTHETIC_FUV=14.60  
    -022226.79                           DEC=-02D22'26.66" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.004848828524888103                    0.00853                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
186 WDJ025251.00 STAR, DA                RA=02H52M50.9709S +/- 0.05",     J2000             V = 14.79 +/- 0.003 SYNTHETIC_FUV=14.60 
    -022517.99                           DEC=-02D25'17.76" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 6.4": Gaia DR3                 
              5187346124402646272, plx=4mas, Bp=20.97, Rp=19.96. Not an   
              M-dwarf, no concern for BOP. Gaia Teff=5673K                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0019477393851241966                   0.01414                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
187 WDJ201900.44 STAR, DA                RA=20H19M0.6313S +/- 0.05",      J2000             V = 15.31 +/- 0.003 SYNTHETIC_FUV=14.64 
    +401649.99                           DEC=+40D16'50.65" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: K-type cpm at 5.3": Gaia DR3 2062283217823775744, Bp=12.07, 
              Rp=10.64, Gaia Teff=4457K                                   

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.011848869039120581                     0.04113                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
188 WDJ133110.86 STAR, DA                RA=13H31M10.8105S +/- 0.05",     J2000             V = 15.12 +/- 0.003 GALEX_FUV=14.77     
    +340841.43                           DEC=+34D08'40.57" +/- 0.05"                        SYNTHETIC_FUV=14.64                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0028628149346898767                   -0.05392                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
189 WDJ023802.20 STAR, DA                RA=02H38M2.2789S +/- 0.05",      J2000             V = 15.4 +/- 0.003 SYNTHETIC_FUV=14.65  
    +221112.94                           DEC=+22D11'12.76" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.005151426584666269                     -0.01109                         0.0                     
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 26]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------
190 WDJ120647.61 STAR, DA                RA=12H06M47.5336S +/- 0.05",     J2000             V = 15.6 +/- 0.003 GALEX_FUV=14.74      
    -323433.11                           DEC=-32D34'33.57" +/- 0.05"                        SYNTHETIC_FUV=14.65                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0050410709556463545                   -0.02854                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
191 WDJ111658.44 STAR, DA                RA=11H16M58.3830S +/- 0.05",     J2000             V = 15.91 +/- 0.003 GALEX_FUV=16.71     
    -163754.10                           DEC=-16D37'54.34" +/- 0.05"                        SYNTHETIC_FUV=14.65                     
    Reference Frame: ICRS    Extended: NO
    Comments: Red cpm at 4.6": Gaia DR3 3558816674631416704, Bp=10.94,    
              Rp=9.71, Gaia Teff=4457K                                    

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0033835541695759926                   -0.015220000000000001            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
192 WDJ130130.71 STAR, DA                RA=13H01M31.3367S +/- 0.05",     J2000             V = 15.24 +/- 0.003 SYNTHETIC_FUV=14.66 
    -723447.50                           DEC=-72D34'47.92" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background objects at 5.3": Gaia DR3                
              5840399578259078400, plx=0.8mas, Bp=20.50, Rp=19.23. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.03927302983320275                      -0.02628                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
193 WDJ223531.08 STAR, DA                RA=22H35M31.5459S +/- 0.05",     J2000             V = 15.11 +/- 0.003 SYNTHETIC_FUV=14.67 
    -571626.63                           DEC=-57D16'26.59" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.029075186375618896                     0.00262                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
194 WDJ083523.43 STAR, DA                RA=08H35M23.4179S +/- 0.05",     J2000             V = 15.32 +/- 0.003 SYNTHETIC_FUV=14.67 
    -435958.23                           DEC=-43D59'58.01" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Two distant (17-21th mag) background objects within 9".     
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -5.959112407454156E-4                    0.013890000000000001             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 27]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
195 WDJ002001.81 STAR, DA                RA=00H20M1.8599S +/- 0.05",      J2000             V = 15.34 +/- 0.003 SYNTHETIC_FUV=14.67 
    +135247.96                           DEC=+13D52'47.92" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.003351873461931599                     -0.00228                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
196 WDJ223621.10 STAR, DA                RA=22H36M21.2077S +/- 0.05",     J2000             V = 15.55 +/- 0.003 GALEX_FUV=14.79     
    -195224.21                           DEC=-19D52'25.36" +/- 0.05"                        SYNTHETIC_FUV=14.68                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0067847370873781385                    -0.07208                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
197 WDJ231459.20 STAR, DA                RA=23H14M59.2590S +/- 0.05",     J2000             V = 16.3 +/- 0.003 GALEX_FUV=14.86      
    -220821.70                           DEC=-22D08'21.58" +/- 0.05"                        SYNTHETIC_FUV=14.68                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0036857496883980524                    0.0075                           0.0                     
------------------------------------------------------------------------------------------------------------------------------------
198 WDJ170900.98 STAR, DA                RA=17H09M1.0543S +/- 0.05",      J2000             V = 15.46 +/- 0.003 SYNTHETIC_FUV=14.68 
    -510117.25                           DEC=-51D01'16.36" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Crowded target area, 14 faint (19-20th mag) background      
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.004737432978783156                     0.05557                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
199 WDJ152738.36 STAR, DA                RA=15H27M38.3741S +/- 0.05",     J2000             V = 15.48 +/- 0.003 SYNTHETIC_FUV=14.68 
    -450207.41                           DEC=-45D02'8.12" +/- 0.05"                                                                 
    Reference Frame: ICRS    Extended: NO
    Comments: Faint background object at 1": Gaia DR3                     
              5999693902331602176, G=20. Not an M-dwarf, no concern for   
              BOP.                                                        

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               9.292442790283044E-4                     -0.04487                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 28]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
200 WDJ151103.63 STAR, DA                RA=15H11M3.5515S +/- 0.05",      J2000             V = 15.15 +/- 0.003 GALEX_FUV=14.84     
    +765348.60                           DEC=+76D53'48.46" +/- 0.05"                        SYNTHETIC_FUV=14.68                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.005125585702566187                    -0.00843                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
202 WDJ060308.63 STAR, DA                RA=06H03M8.7167S +/- 0.05",      J2000             V = 15.11 +/- 0.003 SYNTHETIC_FUV=14.70 
    +451828.83                           DEC=+45D18'27.79" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 8.1": Gaia DR3                 
              962995581171595392, plx=0.08mas, Bp=20.12, Rp=19.07. Not an 
              M-dwarf, no concern for BOP. Gaia Teff=5673K                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.005602169758136376                     -0.06548000000000001             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
203 WDJ205109.94 STAR, DA                RA=20H51M10.1771S +/- 0.05",     J2000             V = 16.03 +/- 0.003 SYNTHETIC_FUV=14.70 
    -753824.15                           DEC=-75D38'24.13" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.015028781036633417                     9.9E-4                           0.0                     
------------------------------------------------------------------------------------------------------------------------------------
204 WDJ180228.51 STAR, DA                RA=18H02M28.4935S +/- 0.05",     J2000             V = 15.08 +/- 0.003 SYNTHETIC_FUV=14.71 
    +005918.54                           DEC=+00D59'19.16" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Crowded target area, four faint (19-20th mag) background    
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0012435184545606266                   0.039229999999999994             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
205 WDJ001717.99 STAR, DA                RA=00H17M17.8841S +/- 0.05",     J2000             V = 15.12 +/- 0.003 SYNTHETIC_FUV=14.71 
    -192013.05                           DEC=-19D20'13.47" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: K-type cpm at 7.5": Gaia DR3 2365377410625322112, Bp=10.41, 
              Rp=9.30, Gaia Teff=4840K                                    

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.006745183481599505                    -0.02622                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 29]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
206 WDJ042842.36 STAR, DA                RA=04H28M42.4817S +/- 0.05",     J2000             V = 15.4 +/- 0.003 GALEX_FUV=14.80      
    -100448.40                           DEC=-10D04'48.95" +/- 0.05"                        SYNTHETIC_FUV=14.71                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.007357574997420339                     -0.03411                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
207 WDJ000538.55 STAR, DA                RA=00H05M38.5166S +/- 0.05",     J2000             V = 15.51 +/- 0.003 GALEX_FUV=14.80     
    -600031.75                           DEC=-60D00'31.04" +/- 0.05"                        SYNTHETIC_FUV=14.73                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.001908497470875432                    0.04442                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
208 WDJ213333.32 STAR, DA                RA=21H33M33.3744S +/- 0.05",     J2000             V = 16.35 +/- 0.003 GALEX_FUV=15.02     
    +352925.65                           DEC=+35D29'25.45" +/- 0.05"                        SYNTHETIC_FUV=14.73                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.003339012534742288                     -0.0125                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
209 WDJ092224.63 STAR, DA                RA=09H22M24.4312S +/- 0.05",     J2000             V = 15.52 +/- 0.003 SYNTHETIC_FUV=14.75 
    -314137.16                           DEC=-31D41'35.85" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 4.3": Gaia DR3                 
              5631320669067017344, plx=0.5mas, Bp=19.41, Rp=18.14. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.012134992952086011                    0.08216                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
210 WDJ003340.89 STAR, DA                RA=00H33M40.9267S +/- 0.05",     J2000             V = 15.74 +/- 0.003 SYNTHETIC_FUV=14.75 
    +555145.28                           DEC=+55D51'45.06" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Two distant (20th mag) background objects within 9".        
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.002258334194153872                     -0.013869999999999999            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 30]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
211 WDJ123213.30 STAR, DA                RA=12H32M13.1376S +/- 0.05",     J2000             V = 15.69 +/- 0.003 GALEX_FUV=14.39     
    -040925.74                           DEC=-04D09'25.71" +/- 0.05"                        SYNTHETIC_FUV=14.75                     
    Reference Frame: ICRS    Extended: NO
    Comments: Two cpm companions:                                         
              At 2.4" Gaia DR3 3681220906103896064, Bp=15.54, Rp=15.72,   
              another white dwarf.                                        
              At 7.1" Gaia DR3 3681220906103896192, Bp=8.79, Rp=8.34,     
              G-type (Gaia Teff=5944K)                                    

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.010263670571050765                    0.00145                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
212 WDJ152131.86 STAR, DA                RA=15H21M31.9008S +/- 0.05",     J2000             V = 15.77 +/- 0.003 GALEX_FUV=14.98     
    +381246.36                           DEC=+38D12'45.59" +/- 0.05"                        SYNTHETIC_FUV=14.75                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.002300225141138593                     -0.04813                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
213 WDJ084747.35 STAR, DA                RA=08H47M46.9481S +/- 0.05",     J2000             V = 15.27 +/- 0.003 SYNTHETIC_FUV=14.75 
    -731249.75                           DEC=-73D12'48.78" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.02519574394986961                     0.06042                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
214 WDJ184225.24 STAR, DA                RA=18H42M25.8889S +/- 0.05",     J2000             V = 15.4 +/- 0.003 SYNTHETIC_FUV=14.75  
    -780505.16                           DEC=-78D05'10.15" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.04084466593768262                      -0.31189999999999996             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
215 WDJ200823.87 STAR, DA                RA=20H08M23.8012S +/- 0.05",     J2000             V = 15.89 +/- 0.003 GALEX_FUV=14.83     
    -660437.71                           DEC=-66D04'37.66" +/- 0.05"                        SYNTHETIC_FUV=14.76                     
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 4.0": Gaia DR3                 
              6427468556179836544, plx=1.5mas, Bp=20.92, Rp=18.91. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.004461909343690004                    0.00325                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
216 WDJ044759.97 STAR, DA                RA=04H48M0.2056S +/- 0.05",      J2000             V = 15.5 +/- 0.003 SYNTHETIC_FUV=14.76  
    +554609.21                           DEC=+55D46'6.32" +/- 0.05"                                                                 
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.014529359733909283                     -0.18051                         0.0                     
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 31]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------
217 WDJ141651.40 STAR, DA                RA=14H16M50.9448S +/- 0.05",     J2000             V = 15.27 +/- 0.003 SYNTHETIC_FUV=14.76 
    -705932.04                           DEC=-70D59'33.56" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Two distant (19-20th mag) background objects within 9".     
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.028370592773901204                    -0.09504                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
218 WDJ123226.19 STAR, DA                RA=12H32M26.0431S +/- 0.05",     J2000             V = 15.74 +/- 0.003 GALEX_FUV=14.95     
    +412919.33                           DEC=+41D29'19.48" +/- 0.05"                        SYNTHETIC_FUV=14.77                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.009423040662466152                    0.00922                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
219 WDJ220113.96 STAR, DA                RA=22H01M14.0256S +/- 0.05",     J2000             V = 15.84 +/- 0.003 GALEX_FUV=14.81     
    -220714.92                           DEC=-22D07'15.27" +/- 0.05"                        SYNTHETIC_FUV=14.77                     
    Reference Frame: ICRS    Extended: NO
    Comments: Two distant (17-20th mag) background objects within 9".     
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.00394361801676736                      -0.022                           0.0                     
------------------------------------------------------------------------------------------------------------------------------------
220 WDJ051613.96 STAR, DA                RA=05H16M13.9649S +/- 0.05",     J2000             V = 15.4 +/- 0.003 SYNTHETIC_FUV=14.77  
    -701934.93                           DEC=-70D19'33.70" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Crowded target area, 14 faint (18-20th mag) background      
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               4.297018537908214E-4                     0.07645                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 32]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
221 WDJ205525.69 STAR, DA                RA=20H55M25.7571S +/- 0.05",     J2000             V = 15.35 +/- 0.003 GALEX_FUV=14.82     
    -225720.39                           DEC=-22D57'21.45" +/- 0.05"                        SYNTHETIC_FUV=14.78                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.004082659886849556                     -0.06664                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
222 WDJ170120.99 STAR, DA                RA=17H01M20.9493S +/- 0.05",     J2000             V = 15.22 +/- 0.003 SYNTHETIC_FUV=14.79 
    -191527.57                           DEC=-19D15'27.40" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Two distant (17-20th mag) background objects within 9".     
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.002788002051748357                    0.01048                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
223 WDJ210428.02 STAR, DA                RA=21H04M27.9237S +/- 0.05",     J2000             V = 15.73 +/- 0.003 GALEX_FUV=14.81     
    -031344.84                           DEC=-03D13'46.60" +/- 0.05"                        SYNTHETIC_FUV=14.80                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.00606563355047746                     -0.11025                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
224 WDJ203645.86 STAR, DA                RA=20H36M45.9098S +/- 0.05",     J2000             V = 15.07 +/- 0.003 GALEX_FUV=15.60     
    -251440.75                           DEC=-25D14'43.10" +/- 0.05"                        SYNTHETIC_FUV=14.80                     
    Reference Frame: ICRS    Extended: NO
    Comments: Faint background object at 7.7": Gaia DR3                   
              6800380775282901504, G=20.9. Not an M-dwarf, no concern for 
              BOP.                                                        

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.002866440094380607                     -0.14711000000000002             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
225 WDJ073504.07 STAR, DA                RA=07H35M4.1049S +/- 0.05",      J2000             V = 16.56 +/- 0.003 GALEX_FUV=15.95     
    -794410.69                           DEC=-79D44'10.81" +/- 0.05"                        SYNTHETIC_FUV=14.80                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.002110246763330849                     -0.00791                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 33]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
226 WDJ092008.26 STAR, DA                RA=09H20M8.1808S +/- 0.05",      J2000             V = 16.47 +/- 0.003 GALEX_FUV=15.01     
    -400400.80                           DEC=-40D03'59.97" +/- 0.05"                        SYNTHETIC_FUV=14.81                     
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 8.7": Gaia DR3                 
              5429478818437959552, plx=0.2mas, Bp=17.22, Rp=16.24, Gaia   
              Teff=6058K. Not an M-dwarf, no concern for BOP.             

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.00500111437691484                     0.05188                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
227 WDJ040607.08 STAR, DA                RA=04H06M6.9146S +/- 0.05",      J2000             V = 15.37 +/- 0.003 SYNTHETIC_FUV=14.82 
    +543132.19                           DEC=+54D31'32.45" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.010252645828159693                    0.016190000000000003             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
228 WDJ162044.87 STAR, DA                RA=16H20M44.8328S +/- 0.05",     J2000             V = 15.38 +/- 0.003 SYNTHETIC_FUV=14.82 
    -190133.35                           DEC=-19D01'33.99" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 3.7": Gaia DR3                 
              6245217082172473344, plx=0.1mas, Bp=20.13, Rp=19.57. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0025351622676940285                   -0.04025                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
229 WDJ182227.62 STAR, DA                RA=18H22M27.6611S +/- 0.05",     J2000             V = 16.46 +/- 0.003 GALEX_FUV=15.10     
    +532331.99                           DEC=+53D23'32.58" +/- 0.05"                        SYNTHETIC_FUV=14.82                     
    Reference Frame: ICRS    Extended: NO
    Comments: Faint background object at 7.5": Gaia DR3                   
              2148495031195344768, G=20.97. Not an M-dwarf, no concern    
              for BOP.                                                    

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.00284852703880258                      0.03694                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
230 WDJ090515.08 STAR, DA                RA=09H05M15.0389S +/- 0.05",     J2000             V = 15.51 +/- 0.003 GALEX_FUV=14.97     
    -234257.31                           DEC=-23D42'56.80" +/- 0.05"                        SYNTHETIC_FUV=14.83                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0022842324896600154                   0.03202                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 34]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
231 WDJ213712.53 STAR, DA                RA=21H37M12.5204S +/- 0.05",     J2000             V = 16.06 +/- 0.003 SYNTHETIC_FUV=14.84 
    +473459.98                           DEC=+47D34'59.41" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Crowded target area, 5 faint (16.5-20th mag) background     
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -7.04699403457948E-4                     -0.03523                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
232 WDJ235223.18 STAR, DA                RA=23H52M23.2272S +/- 0.05",     J2000             V = 15.48 +/- 0.003 SYNTHETIC_FUV=14.84 
    -280316.01                           DEC=-28D03'16.88" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.002795092622548222                     -0.05428                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
233 WDJ143526.31 STAR, DA                RA=14H35M26.3009S +/- 0.05",     J2000             V = 15.52 +/- 0.003 GALEX_FUV=15.10     
    -055027.99                           DEC=-05D50'28.26" +/- 0.05"                        SYNTHETIC_FUV=14.84                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -4.2219209986588363E-4                   -0.01746                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
234 WDJ083152.65 STAR, DA                RA=08H31M52.5901S +/- 0.05",     J2000             V = 15.45 +/- 0.003 SYNTHETIC_FUV=14.85 
    -261207.15                           DEC=-26D12'7.43" +/- 0.05"                                                                 
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.003943192767562606                    -0.01725                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
235 WDJ082246.16 STAR, DA                RA=08H22M46.0687S +/- 0.05",     J2000             V = 15.61 +/- 0.003 GALEX_FUV=15.04     
    +361412.61                           DEC=+36D14'11.68" +/- 0.05"                        SYNTHETIC_FUV=14.85                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.005959295013496517                    -0.05823                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
236 WDJ100337.51 STAR, DA                RA=10H03M37.5563S +/- 0.05",     J2000             V = 15.52 +/- 0.003 GALEX_FUV=15.06     
    -451553.74                           DEC=-45D15'53.69" +/- 0.05"                        SYNTHETIC_FUV=14.86                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.002856751088215838                     0.00272                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 35]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
237 WDJ102228.77 STAR, DA                RA=10H22M28.6929S +/- 0.05",     J2000             V = 15.65 +/- 0.003 GALEX_FUV=15.04     
    +124159.40                           DEC=+12D41'58.60" +/- 0.05"                        SYNTHETIC_FUV=14.86                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.004921055182985312                    -0.0506                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
238 WDJ062117.23 STAR, DA                RA=06H21M17.2895S +/- 0.05",     J2000             V = 15.76 +/- 0.003 GALEX_FUV=15.08     
    +370023.14                           DEC=+37D00'23.13" +/- 0.05"                        SYNTHETIC_FUV=14.86                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0036398485756031955                    -0.001                           0.0                     
------------------------------------------------------------------------------------------------------------------------------------
239 WDJ201501.62 STAR, DA                RA=20H15M1.6808S +/- 0.05",      J2000             V = 15.7 +/- 0.003 SYNTHETIC_FUV=14.87  
    -565007.53                           DEC=-56D50'8.67" +/- 0.05"                                                                 
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.003598754352918607                     -0.07061                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
240 WDJ002959.00 STAR, DA                RA=00H29M59.1172S +/- 0.05",     J2000             V = 16.43 +/- 0.003 GALEX_FUV=15.02     
    +364834.86                           DEC=+36D48'34.13" +/- 0.05"                        SYNTHETIC_FUV=14.87                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.007572348892714208                     -0.045869999999999994            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
241 WDJ101420.66 STAR, DA                RA=10H14M20.6141S +/- 0.05",     J2000             V = 16.35 +/- 0.003 GALEX_FUV=14.98     
    -041721.08                           DEC=-04D17'21.27" +/- 0.05"                        SYNTHETIC_FUV=14.88                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0026554373633673476                   -0.01252                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
242 WDJ235857.81 STAR, DA                RA=23H58M57.7335S +/- 0.05",     J2000             V = 15.4 +/- 0.003 GALEX_FUV=14.94      
    -445713.44                           DEC=-44D57'13.64" +/- 0.05"                        SYNTHETIC_FUV=14.88                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.004625463296155577                    -0.012960000000000001            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
244 WDJ235200.03 STAR, DA                RA=23H52M0.1042S +/- 0.05",      J2000             V = 15.59 +/- 0.003 GALEX_FUV=15.00     
    -033654.01                           DEC=-03D36'53.69" +/- 0.05"                        SYNTHETIC_FUV=14.90                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.004406099927993509                     0.020149999999999998             0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 36]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
245 WDJ113842.69 STAR, DA                RA=11H38M42.7347S +/- 0.05",     J2000             V = 15.85 +/- 0.003 SYNTHETIC_FUV=14.90 
    -584424.06                           DEC=-58D44'24.27" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Crowded target area, 6 faint (17-20th mag) background       
              objects within 9".                                          
              None of them should cause any concern regarding the target  
              acquisition or BOP limits.                                  
              None of these are M-dwarfs (all have small parallaxes,      
              small proper motions).                                      

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0029021739507694255                    -0.01309                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
246 WDJ212418.93 STAR, DA                RA=21H24M19.8043S +/- 0.05",     J2000             V = 15.5 +/- 0.003 GALEX_FUV=15.57      
    +855645.12                           DEC=+85D56'45.90" +/- 0.05"                        SYNTHETIC_FUV=14.90                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0545440345260789                       0.04819                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
247 WDJ083637.32 STAR, DA                RA=08H36M37.3475S +/- 0.05",     J2000             V = 15.68 +/- 0.003 SYNTHETIC_FUV=14.91 
    -281638.66                           DEC=-28D16'39.38" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 8.5": Gaia DR3                 
              5645707297680599040, plx=0.3mas, Bp=20.50, Rp=19.40. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0020340745253534204                    -0.04494                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
248 WDJ090638.59 STAR, DA                RA=09H06M38.5901S +/- 0.05",     J2000             V = 15.42 +/- 0.003 GALEX_FUV=15.04     
    +070059.81                           DEC=+07D00'59.22" +/- 0.05"                        SYNTHETIC_FUV=14.91                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               8.93356908247734E-5                      -0.03642                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
249 WDJ124752.77 STAR, DA                RA=12H47M52.6518S +/- 0.05",     J2000             V = 15.3 +/- 0.003 GALEX_FUV=15.06      
    -412810.27                           DEC=-41D28'10.49" +/- 0.05"                        SYNTHETIC_FUV=14.92                     
    Reference Frame: ICRS    Extended: NO
    Comments: Distant background object at 7.0": Gaia DR3                 
              6139927603884664576, plx=0.3mas, Bp=18.04, Rp=16.92. Not an 
              M-dwarf, no concern for BOP.                                

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.0071933093224443604                   -0.013529999999999999            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 37]

TARGET LIST    Fixed Targets
------------------------------------------------------------------------------------------------------------------------------------
Tar|   Target   |         Target        |            Target              |Coord   | Radial |             Flux data
No |    Name    |       Description     |           Position             |Eqnx    |  Vel.  |
------------------------------------------------------------------------------------------------------------------------------------
250 WDJ132230.90 STAR, DA                RA=13H22M30.8191S +/- 0.05",     J2000             V = 15.17 +/- 0.003 GALEX_FUV=14.90     
    -061158.15                           DEC=-06D12'0.43" +/- 0.05"                         SYNTHETIC_FUV=14.92                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.004799406314355624                    -0.14114                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
251 WDJ211146.39 STAR, DA                RA=21H11M46.4483S +/- 0.05",     J2000             V = 15.24 +/- 0.003 GALEX_FUV=15.01     
    +012054.26                           DEC=+01D20'53.52" +/- 0.05"                        SYNTHETIC_FUV=14.93                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0038977456800846624                    -0.046009999999999995            0.0                     
------------------------------------------------------------------------------------------------------------------------------------
252 WDJ085708.32 STAR, DA                RA=08H57M8.0740S +/- 0.05",      J2000             V = 15.52 +/- 0.003 SYNTHETIC_FUV=14.93 
    -603245.24                           DEC=-60D32'41.58" +/- 0.05"                                                                
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               -0.015451204279261593                    0.2287                           0.0                     
------------------------------------------------------------------------------------------------------------------------------------
253 WDJ031743.17 STAR, DA                RA=03H17M43.2379S +/- 0.05",     J2000             V = 15.84 +/- 0.003 GALEX_FUV=15.17     
    +090955.15                           DEC=+09D09'55.01" +/- 0.05"                        SYNTHETIC_FUV=14.93                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.004448797951085901                     -0.00856                         0.0                     
------------------------------------------------------------------------------------------------------------------------------------
254 WDJ074735.98 STAR, DA                RA=07H47M36.0004S +/- 0.05",     J2000             V = 15.79 +/- 0.003 GALEX_FUV=15.05     
    +210635.83                           DEC=+21D06'36.25" +/- 0.05"                        SYNTHETIC_FUV=14.93                     
    Reference Frame: ICRS    Extended: NO

   Epoch of Position    RA proper motion (seconds of time/yr)    DEC Proper Motion (arcsec/yr)    Annual Parallax (arcsec)
   2016.0               0.0013492119388078515                    0.02628                          0.0                     
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 38]

Visit: 01 (WDJ013139.22-201958.63)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ013139.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     2-201958.63          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ013139.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     2-201958.63          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ013139.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=645, FLASH=YES,    1   755 S (755                          
     2-201958.63          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ013139.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=645, FLASH=YES,    1   755 S (755                          
     2-201958.63          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ013139.22-201958 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                KXD                                                                                              
WDJ013139.22-201958 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                KD                                                                                               
WDJ013139.22-201958 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                G                                                                                                
WDJ013139.22-201958 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 39]

Visit: 02 (WDJ162044.87-190133.35 #2)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ162044.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     7-190133.35          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ162044.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     7-190133.35          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ162044.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=281, FLASH=YES,    1   281 S (281                          
     7-190133.35          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ162044.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=281, FLASH=YES,    1   281 S (281                          
     7-190133.35          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ162044.87-190133 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                KXD                                                                                              
WDJ162044.87-190133 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                KD                                                                                               
WDJ162044.87-190133 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                G                                                                                                
WDJ162044.87-190133 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 40]

Visit: 03 (WDJ031715.85-853225.56)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ031715.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     5-853225.56          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ031715.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     5-853225.56          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ031715.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=130, FLASH=YES,    1   500 S (500                          
     5-853225.56          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ031715.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=130, FLASH=YES,    1   500 S (500                          
     5-853225.56          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ031715.85-853225 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.56                                KXD                                                                                              
WDJ031715.85-853225 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.56                                KD                                                                                               
WDJ031715.85-853225 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.56                                G                                                                                                
WDJ031715.85-853225 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.56                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 41]

Visit: 04 (WDJ031719.13-853231.29)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ031719.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     3-853231.29          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ031719.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     3-853231.29          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ031719.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=245, FLASH=YES,    1   600 S (600                          
     3-853231.29          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ031719.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=245, FLASH=YES,    1   600 S (600                          
     3-853231.29          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ031719.13-853231 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.29                                KXD                                                                                              
WDJ031719.13-853231 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.29                                KD                                                                                               
WDJ031719.13-853231 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.29                                G                                                                                                
WDJ031719.13-853231 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.29                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 42]

Visit: 05 (WDJ040223.78+320153.80)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ040223.7 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     8+320153.80          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ040223.7 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     8+320153.80          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ040223.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=130, FLASH=YES,    1   500 S (500                          
     8+320153.80          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ040223.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=130, FLASH=YES,    1   500 S (500                          
     8+320153.80          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ040223.78+320153 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                KXD                                                                                              
WDJ040223.78+320153 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                KD                                                                                               
WDJ040223.78+320153 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                G                                                                                                
WDJ040223.78+320153 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 43]

Visit: 06 (WDJ043659.47+253547.49)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ043659.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     7+253547.49          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ043659.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     7+253547.49          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ043659.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=665, FLASH=YES,    1   775 S (775                          
     7+253547.49          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ043659.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=665, FLASH=YES,    1   775 S (775                          
     7+253547.49          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ043659.47+253547 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.49                                KXD                                                                                              
WDJ043659.47+253547 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.49                                KD                                                                                               
WDJ043659.47+253547 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.49                                G                                                                                                
WDJ043659.47+253547 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.49                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 44]

Visit: 08 (WDJ050940.99+015308.63)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ050940.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     9+015308.63          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ050940.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     9+015308.63          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ050940.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=430, FLASH=YES,    1   540 S (540                          
     9+015308.63          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ050940.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=430, FLASH=YES,    1   540 S (540                          
     9+015308.63          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ050940.99+015308 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                KXD                                                                                              
WDJ050940.99+015308 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                KD                                                                                               
WDJ050940.99+015308 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                G                                                                                                
WDJ050940.99+015308 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 45]

Visit: 09 (WDJ040607.08+543132.19 #2)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ040607.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     8+543132.19          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ040607.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     8+543132.19          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ040607.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=790, FLASH=YES,    1   900 S (900                          
     8+543132.19          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ040607.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=790, FLASH=YES,    1   900 S (900                          
     8+543132.19          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ040607.08+543132 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.19                                KXD                                                                                              
WDJ040607.08+543132 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.19                                KD                                                                                               
WDJ040607.08+543132 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.19                                G                                                                                                
WDJ040607.08+543132 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.19                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 46]

Visit: 0A (WDJ151103.63+765348.60)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ151103.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3+765348.60          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ151103.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3+765348.60          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ151103.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+765348.60          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ151103.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+765348.60          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ151103.63+765348 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.60                                KXD                                                                                              
WDJ151103.63+765348 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.60                                KD                                                                                               
WDJ151103.63+765348 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.60                                G                                                                                                
WDJ151103.63+765348 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.60                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 47]

Visit: 0B (WDJ234331.84-882310.21 #2)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: This is a repeat of Visit 34, which failed because the Fine Guidance Sensors did not        
                          acquire the guide stars. The target of this visit has been BOP cleared.                     


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ234331.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     4-882310.21          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ234331.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     4-882310.21          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ234331.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=180, FLASH=YES,    1   290 S (290                          
     4-882310.21          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ234331.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=180, FLASH=YES,    1   290 S (290                          
     4-882310.21          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ234331.84-882310 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KXD                                                                                              
WDJ234331.84-882310 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KD                                                                                               
WDJ234331.84-882310 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
WDJ234331.84-882310 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 48]

Visit: 0C (WDJ060308.63+451828.83)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ060308.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3+451828.83          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ060308.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3+451828.83          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ060308.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+451828.83          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ060308.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+451828.83          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ060308.63+451828 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                KXD                                                                                              
WDJ060308.63+451828 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                KD                                                                                               
WDJ060308.63+451828 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                G                                                                                                
WDJ060308.63+451828 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 49]

Visit: 0D (WDJ205109.94-753824.15)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ205109.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     4-753824.15          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ205109.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     4-753824.15          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ205109.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-753824.15          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ205109.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-753824.15          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ205109.94-753824 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                KXD                                                                                              
WDJ205109.94-753824 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                KD                                                                                               
WDJ205109.94-753824 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                G                                                                                                
WDJ205109.94-753824 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 50]

Visit: 0E (WDJ180228.51+005918.54)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ180228.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     1+005918.54          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ180228.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     1+005918.54          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ180228.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1+005918.54          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ180228.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1+005918.54          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ180228.51+005918 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.54                                KXD                                                                                              
WDJ180228.51+005918 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.54                                KD                                                                                               
WDJ180228.51+005918 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.54                                G                                                                                                
WDJ180228.51+005918 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.54                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 51]

Visit: 0F (WDJ001717.99-192013.05)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ001717.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     9-192013.05          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ001717.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     9-192013.05          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ001717.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9-192013.05          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ001717.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9-192013.05          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ001717.99-192013 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.05                                KXD                                                                                              
WDJ001717.99-192013 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.05                                KD                                                                                               
WDJ001717.99-192013 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.05                                G                                                                                                
WDJ001717.99-192013 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.05                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 52]

Visit: 0G (WDJ042842.36-100448.40)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ042842.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     6-100448.40          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ042842.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     6-100448.40          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ042842.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-100448.40          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ042842.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-100448.40          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ042842.36-100448 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.40                                KXD                                                                                              
WDJ042842.36-100448 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.40                                KD                                                                                               
WDJ042842.36-100448 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.40                                G                                                                                                
WDJ042842.36-100448 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.40                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 53]

Visit: 0H (WDJ000538.55-600031.75)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ000538.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     5-600031.75          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ000538.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     5-600031.75          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ000538.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     5-600031.75          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ000538.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     5-600031.75          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ000538.55-600031 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                KXD                                                                                              
WDJ000538.55-600031 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                KD                                                                                               
WDJ000538.55-600031 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                G                                                                                                
WDJ000538.55-600031 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 54]

Visit: 0I (WDJ213333.32+352925.65)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ213333.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     2+352925.65          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ213333.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     2+352925.65          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ213333.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2+352925.65          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ213333.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2+352925.65          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ213333.32+352925 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.65                                KXD                                                                                              
WDJ213333.32+352925 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.65                                KD                                                                                               
WDJ213333.32+352925 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.65                                G                                                                                                
WDJ213333.32+352925 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.65                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 55]

Visit: 0J (WDJ092224.63-314137.16)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ092224.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3-314137.16          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ092224.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3-314137.16          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ092224.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-314137.16          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ092224.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-314137.16          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ092224.63-314137 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                KXD                                                                                              
WDJ092224.63-314137 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                KD                                                                                               
WDJ092224.63-314137 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                G                                                                                                
WDJ092224.63-314137 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 56]

Visit: 0K (WDJ003340.89+555145.28)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ003340.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     9+555145.28          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ003340.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     9+555145.28          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ003340.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9+555145.28          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ003340.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9+555145.28          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ003340.89+555145 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.28                                KXD                                                                                              
WDJ003340.89+555145 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.28                                KD                                                                                               
WDJ003340.89+555145 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.28                                G                                                                                                
WDJ003340.89+555145 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.28                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 57]

Visit: 0L (WDJ123213.30-040925.74)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ123213.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     0-040925.74          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ123213.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     0-040925.74          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ123213.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-040925.74          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ123213.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-040925.74          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ123213.30-040925 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                KXD                                                                                              
WDJ123213.30-040925 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                KD                                                                                               
WDJ123213.30-040925 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                G                                                                                                
WDJ123213.30-040925 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 58]

Visit: 0M (WDJ152131.86+381246.36)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ152131.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     6+381246.36          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ152131.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     6+381246.36          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ152131.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6+381246.36          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ152131.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6+381246.36          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ152131.86+381246 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.36                                KXD                                                                                              
WDJ152131.86+381246 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.36                                KD                                                                                               
WDJ152131.86+381246 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.36                                G                                                                                                
WDJ152131.86+381246 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.36                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 59]

Visit: 0N (WDJ084747.35-731249.75)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ084747.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     5-731249.75          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ084747.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     5-731249.75          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ084747.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     5-731249.75          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ084747.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     5-731249.75          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ084747.35-731249 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                KXD                                                                                              
WDJ084747.35-731249 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                KD                                                                                               
WDJ084747.35-731249 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                G                                                                                                
WDJ084747.35-731249 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 60]

Visit: 0O (WDJ184225.24-780505.16)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ184225.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     4-780505.16          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ184225.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     4-780505.16          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ184225.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-780505.16          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ184225.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-780505.16          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ184225.24-780505 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                KXD                                                                                              
WDJ184225.24-780505 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                KD                                                                                               
WDJ184225.24-780505 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                G                                                                                                
WDJ184225.24-780505 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 61]

Visit: 0P (WDJ200823.87-660437.71)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ200823.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     7-660437.71          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ200823.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     7-660437.71          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ200823.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7-660437.71          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ200823.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7-660437.71          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ200823.87-660437 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.71                                KXD                                                                                              
WDJ200823.87-660437 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.71                                KD                                                                                               
WDJ200823.87-660437 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.71                                G                                                                                                
WDJ200823.87-660437 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.71                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 62]

Visit: 0Q (WDJ044759.97+554609.21)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ044759.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     7+554609.21          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ044759.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     7+554609.21          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ044759.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7+554609.21          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ044759.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7+554609.21          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ044759.97+554609 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KXD                                                                                              
WDJ044759.97+554609 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KD                                                                                               
WDJ044759.97+554609 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
WDJ044759.97+554609 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 63]

Visit: 0R (WDJ141651.40-705932.04)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ141651.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     0-705932.04          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ141651.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     0-705932.04          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ141651.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-705932.04          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ141651.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-705932.04          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ141651.40-705932 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.04                                KXD                                                                                              
WDJ141651.40-705932 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.04                                KD                                                                                               
WDJ141651.40-705932 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.04                                G                                                                                                
WDJ141651.40-705932 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.04                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 64]

Visit: 0S (WDJ123226.19+412919.33)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ123226.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     9+412919.33          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ123226.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     9+412919.33          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ123226.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9+412919.33          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ123226.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9+412919.33          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ123226.19+412919 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                KXD                                                                                              
WDJ123226.19+412919 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                KD                                                                                               
WDJ123226.19+412919 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                G                                                                                                
WDJ123226.19+412919 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 65]

Visit: 0T (WDJ220113.96-220714.92)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ220113.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     6-220714.92          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ220113.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     6-220714.92          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ220113.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-220714.92          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ220113.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-220714.92          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ220113.96-220714 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.92                                KXD                                                                                              
WDJ220113.96-220714 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.92                                KD                                                                                               
WDJ220113.96-220714 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.92                                G                                                                                                
WDJ220113.96-220714 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.92                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 66]

Visit: 0U (WDJ051613.96-701934.93)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ051613.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     6-701934.93          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ051613.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     6-701934.93          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ051613.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-701934.93          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ051613.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-701934.93          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ051613.96-701934 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.93                                KXD                                                                                              
WDJ051613.96-701934 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.93                                KD                                                                                               
WDJ051613.96-701934 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.93                                G                                                                                                
WDJ051613.96-701934 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.93                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 67]

Visit: 0V (WDJ205525.69-225720.39)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ205525.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     9-225720.39          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ205525.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     9-225720.39          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ205525.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9-225720.39          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ205525.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9-225720.39          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ205525.69-225720 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.39                                KXD                                                                                              
WDJ205525.69-225720 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.39                                KD                                                                                               
WDJ205525.69-225720 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.39                                G                                                                                                
WDJ205525.69-225720 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.39                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 68]

Visit: 0W (WDJ170120.99-191527.57)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ170120.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     9-191527.57          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ170120.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     9-191527.57          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ170120.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9-191527.57          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ170120.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9-191527.57          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ170120.99-191527 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.57                                KXD                                                                                              
WDJ170120.99-191527 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.57                                KD                                                                                               
WDJ170120.99-191527 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.57                                G                                                                                                
WDJ170120.99-191527 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.57                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 69]

Visit: 0X (WDJ210428.02-031344.84)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ210428.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     2-031344.84          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ210428.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     2-031344.84          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ210428.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2-031344.84          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ210428.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2-031344.84          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ210428.02-031344 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.84                                KXD                                                                                              
WDJ210428.02-031344 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.84                                KD                                                                                               
WDJ210428.02-031344 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.84                                G                                                                                                
WDJ210428.02-031344 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.84                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 70]

Visit: 0Y (WDJ203645.86-251440.75)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ203645.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     6-251440.75          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ203645.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     6-251440.75          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ203645.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-251440.75          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ203645.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-251440.75          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ203645.86-251440 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                KXD                                                                                              
WDJ203645.86-251440 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                KD                                                                                               
WDJ203645.86-251440 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                G                                                                                                
WDJ203645.86-251440 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 71]

Visit: 0Z (WDJ073504.07-794410.69)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ073504.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     7-794410.69          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ073504.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     7-794410.69          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ073504.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7-794410.69          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ073504.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7-794410.69          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ073504.07-794410 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.69                                KXD                                                                                              
WDJ073504.07-794410 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.69                                KD                                                                                               
WDJ073504.07-794410 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.69                                G                                                                                                
WDJ073504.07-794410 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.69                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 72]

Visit: 10 (WDJ053343.43-271350.08)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ053343.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     3-271350.08          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ053343.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     3-271350.08          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ053343.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=245, FLASH=YES,    1   600 S (600                          
     3-271350.08          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ053343.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=245, FLASH=YES,    1   600 S (600                          
     3-271350.08          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ053343.43-271350 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                KXD                                                                                              
WDJ053343.43-271350 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                KD                                                                                               
WDJ053343.43-271350 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                G                                                                                                
WDJ053343.43-271350 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 73]

Visit: 12 (WDJ085047.51+172602.06)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ085047.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     1+172602.06          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ085047.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     1+172602.06          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ085047.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=350, FLASH=YES,    1   460 S (460                          
     1+172602.06          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ085047.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=350, FLASH=YES,    1   460 S (460                          
     1+172602.06          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ085047.51+172602 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                KXD                                                                                              
WDJ085047.51+172602 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                KD                                                                                               
WDJ085047.51+172602 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                G                                                                                                
WDJ085047.51+172602 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 74]

Visit: 13 (WDJ100551.52-023417.93)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ100551.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     2-023417.93          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ100551.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     2-023417.93          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ100551.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=520, FLASH=YES,    1   630 S (630                          
     2-023417.93          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ100551.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=520, FLASH=YES,    1   630 S (630                          
     2-023417.93          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ100551.52-023417 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.93                                KXD                                                                                              
WDJ100551.52-023417 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.93                                KD                                                                                               
WDJ100551.52-023417 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.93                                G                                                                                                
WDJ100551.52-023417 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.93                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 75]

Visit: 14 (WDJ101511.71-010416.24)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ101511.7 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     1-010416.24          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ101511.7 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     1-010416.24          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ101511.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=430, FLASH=YES,    1   540 S (540                          
     1-010416.24          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ101511.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=430, FLASH=YES,    1   540 S (540                          
     1-010416.24          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ101511.71-010416 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.24                                KXD                                                                                              
WDJ101511.71-010416 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.24                                KD                                                                                               
WDJ101511.71-010416 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.24                                G                                                                                                
WDJ101511.71-010416 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.24                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 76]

Visit: 15 (WDJ102846.64-214106.70)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ102846.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     4-214106.70          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ102846.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     4-214106.70          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ102846.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=460, FLASH=YES,    1   570 S (570                          
     4-214106.70          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ102846.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=460, FLASH=YES,    1   570 S (570                          
     4-214106.70          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ102846.64-214106 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                KXD                                                                                              
WDJ102846.64-214106 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                KD                                                                                               
WDJ102846.64-214106 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                G                                                                                                
WDJ102846.64-214106 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 77]

Visit: 16 (WDJ104346.70-390637.35)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ104346.7 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     0-390637.35          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ104346.7 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     0-390637.35          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ104346.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=195, FLASH=YES,    1   500 S (500                          
     0-390637.35          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ104346.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=195, FLASH=YES,    1   500 S (500                          
     0-390637.35          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ104346.70-390637 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                KXD                                                                                              
WDJ104346.70-390637 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                KD                                                                                               
WDJ104346.70-390637 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                G                                                                                                
WDJ104346.70-390637 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 78]

Visit: 17 (WDJ120347.43-002310.94)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ120347.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     3-002310.94          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ120347.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     3-002310.94          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ120347.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=415, FLASH=YES,    1   525 S (525                          
     3-002310.94          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ120347.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=415, FLASH=YES,    1   525 S (525                          
     3-002310.94          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ120347.43-002310 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.94                                KXD                                                                                              
WDJ120347.43-002310 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.94                                KD                                                                                               
WDJ120347.43-002310 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.94                                G                                                                                                
WDJ120347.43-002310 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.94                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 79]

Visit: 18 (WDJ133913.54+120831.23)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ133913.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     4+120831.23          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ133913.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     4+120831.23          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ133913.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=625, FLASH=YES,    1   735 S (735                          
     4+120831.23          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ133913.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=625, FLASH=YES,    1   735 S (735                          
     4+120831.23          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ133913.54+120831 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                KXD                                                                                              
WDJ133913.54+120831 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                KD                                                                                               
WDJ133913.54+120831 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                G                                                                                                
WDJ133913.54+120831 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 80]

Visit: 19 (WDJ133915.05-370620.16)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ133915.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     5-370620.16          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ133915.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     5-370620.16          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ133915.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=334, FLASH=YES,    1   444 S (444                          
     5-370620.16          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ133915.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=334, FLASH=YES,    1   444 S (444                          
     5-370620.16          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ133915.05-370620 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                KXD                                                                                              
WDJ133915.05-370620 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                KD                                                                                               
WDJ133915.05-370620 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                G                                                                                                
WDJ133915.05-370620 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 81]

Visit: 1A (WDJ092008.26-400400.80)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ092008.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     6-400400.80          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ092008.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     6-400400.80          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ092008.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-400400.80          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ092008.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-400400.80          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ092008.26-400400 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                KXD                                                                                              
WDJ092008.26-400400 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                KD                                                                                               
WDJ092008.26-400400 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                G                                                                                                
WDJ092008.26-400400 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 82]

Visit: 1B (WDJ040607.08+543132.19)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ040607.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     8+543132.19          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ040607.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     8+543132.19          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ040607.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8+543132.19          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ040607.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8+543132.19          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ040607.08+543132 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.19                                KXD                                                                                              
WDJ040607.08+543132 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.19                                KD                                                                                               
WDJ040607.08+543132 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.19                                G                                                                                                
WDJ040607.08+543132 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.19                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 83]

Visit: 1C (WDJ162044.87-190133.35)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ162044.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     7-190133.35          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ162044.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     7-190133.35          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ162044.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7-190133.35          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ162044.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7-190133.35          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ162044.87-190133 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                KXD                                                                                              
WDJ162044.87-190133 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                KD                                                                                               
WDJ162044.87-190133 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                G                                                                                                
WDJ162044.87-190133 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.35                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 84]

Visit: 1D (WDJ182227.62+532331.99)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ182227.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     2+532331.99          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ182227.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     2+532331.99          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ182227.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2+532331.99          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ182227.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2+532331.99          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ182227.62+532331 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                KXD                                                                                              
WDJ182227.62+532331 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                KD                                                                                               
WDJ182227.62+532331 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                G                                                                                                
WDJ182227.62+532331 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 85]

Visit: 1E (WDJ090515.08-234257.31)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ090515.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     8-234257.31          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ090515.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     8-234257.31          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ090515.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8-234257.31          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ090515.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8-234257.31          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ090515.08-234257 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.31                                KXD                                                                                              
WDJ090515.08-234257 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.31                                KD                                                                                               
WDJ090515.08-234257 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.31                                G                                                                                                
WDJ090515.08-234257 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.31                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 86]

Visit: 1F (WDJ213712.53+473459.98)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ213712.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3+473459.98          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ213712.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3+473459.98          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ213712.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+473459.98          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ213712.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+473459.98          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ213712.53+473459 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                KXD                                                                                              
WDJ213712.53+473459 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                KD                                                                                               
WDJ213712.53+473459 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                G                                                                                                
WDJ213712.53+473459 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 87]

Visit: 1G (WDJ235223.18-280316.01)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ235223.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     8-280316.01          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ235223.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     8-280316.01          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ235223.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8-280316.01          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ235223.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8-280316.01          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ235223.18-280316 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KXD                                                                                              
WDJ235223.18-280316 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KD                                                                                               
WDJ235223.18-280316 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
WDJ235223.18-280316 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 88]

Visit: 1H (WDJ143526.31-055027.99)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ143526.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     1-055027.99          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ143526.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     1-055027.99          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ143526.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-055027.99          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ143526.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-055027.99          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ143526.31-055027 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                KXD                                                                                              
WDJ143526.31-055027 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                KD                                                                                               
WDJ143526.31-055027 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                G                                                                                                
WDJ143526.31-055027 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 89]

Visit: 1I (WDJ083152.65-261207.15)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ083152.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     5-261207.15          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ083152.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     5-261207.15          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ083152.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     5-261207.15          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ083152.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     5-261207.15          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ083152.65-261207 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                KXD                                                                                              
WDJ083152.65-261207 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                KD                                                                                               
WDJ083152.65-261207 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                G                                                                                                
WDJ083152.65-261207 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 90]

Visit: 1J (WDJ082246.16+361412.61)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ082246.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     6+361412.61          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ082246.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     6+361412.61          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ082246.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6+361412.61          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ082246.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6+361412.61          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ082246.16+361412 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.61                                KXD                                                                                              
WDJ082246.16+361412 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.61                                KD                                                                                               
WDJ082246.16+361412 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.61                                G                                                                                                
WDJ082246.16+361412 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.61                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 91]

Visit: 1K (WDJ100337.51-451553.74)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ100337.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     1-451553.74          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ100337.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     1-451553.74          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ100337.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-451553.74          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ100337.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-451553.74          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ100337.51-451553 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                KXD                                                                                              
WDJ100337.51-451553 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                KD                                                                                               
WDJ100337.51-451553 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                G                                                                                                
WDJ100337.51-451553 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 92]

Visit: 1L (WDJ102228.77+124159.40)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ102228.7 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     7+124159.40          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ102228.7 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     7+124159.40          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ102228.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7+124159.40          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ102228.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7+124159.40          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ102228.77+124159 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.40                                KXD                                                                                              
WDJ102228.77+124159 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.40                                KD                                                                                               
WDJ102228.77+124159 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.40                                G                                                                                                
WDJ102228.77+124159 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.40                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 93]

Visit: 1M (WDJ062117.23+370023.14)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ062117.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3+370023.14          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ062117.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3+370023.14          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ062117.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+370023.14          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ062117.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+370023.14          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ062117.23+370023 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.14                                KXD                                                                                              
WDJ062117.23+370023 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.14                                KD                                                                                               
WDJ062117.23+370023 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.14                                G                                                                                                
WDJ062117.23+370023 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.14                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 94]

Visit: 1N (WDJ201501.62-565007.53)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ201501.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     2-565007.53          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ201501.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     2-565007.53          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ201501.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2-565007.53          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ201501.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2-565007.53          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ201501.62-565007 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.53                                KXD                                                                                              
WDJ201501.62-565007 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.53                                KD                                                                                               
WDJ201501.62-565007 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.53                                G                                                                                                
WDJ201501.62-565007 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.53                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 95]

Visit: 1O (WDJ002959.00+364834.86)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ002959.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     0+364834.86          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ002959.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     0+364834.86          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ002959.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0+364834.86          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ002959.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0+364834.86          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ002959.00+364834 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.86                                KXD                                                                                              
WDJ002959.00+364834 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.86                                KD                                                                                               
WDJ002959.00+364834 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.86                                G                                                                                                
WDJ002959.00+364834 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.86                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 96]

Visit: 1P (WDJ101420.66-041721.08)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ101420.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     6-041721.08          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ101420.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     6-041721.08          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ101420.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-041721.08          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ101420.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-041721.08          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ101420.66-041721 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                KXD                                                                                              
WDJ101420.66-041721 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                KD                                                                                               
WDJ101420.66-041721 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                G                                                                                                
WDJ101420.66-041721 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 97]

Visit: 1Q (WDJ235857.81-445713.44)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ235857.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     1-445713.44          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ235857.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     1-445713.44          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ235857.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-445713.44          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ235857.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-445713.44          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ235857.81-445713 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.44                                KXD                                                                                              
WDJ235857.81-445713 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.44                                KD                                                                                               
WDJ235857.81-445713 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.44                                G                                                                                                
WDJ235857.81-445713 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.44                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 98]

Visit: 1R (WDJ235200.03-033654.01 #3)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: This is a repeat of Visit 34, which failed because the Fine Guidance Sensors did not        
                          acquire the guide stars. The target of this visit has been BOP cleared.                     


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ235200.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3-033654.01          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ235200.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3-033654.01          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ235200.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-033654.01          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ235200.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-033654.01          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ235200.03-033654 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KXD                                                                                              
WDJ235200.03-033654 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KD                                                                                               
WDJ235200.03-033654 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
WDJ235200.03-033654 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [ 99]

Visit: 1S (WDJ235200.03-033654.01)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ235200.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3-033654.01          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ235200.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3-033654.01          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ235200.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-033654.01          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ235200.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-033654.01          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ235200.03-033654 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KXD                                                                                              
WDJ235200.03-033654 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KD                                                                                               
WDJ235200.03-033654 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
WDJ235200.03-033654 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [100]

Visit: 1T (WDJ113842.69-584424.06)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ113842.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     9-584424.06          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ113842.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     9-584424.06          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ113842.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9-584424.06          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ113842.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9-584424.06          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ113842.69-584424 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                KXD                                                                                              
WDJ113842.69-584424 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                KD                                                                                               
WDJ113842.69-584424 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                G                                                                                                
WDJ113842.69-584424 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [101]

Visit: 1U (WDJ212418.93+855645.12)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ212418.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3+855645.12          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ212418.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3+855645.12          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ212418.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+855645.12          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ212418.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+855645.12          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ212418.93+855645 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.12                                KXD                                                                                              
WDJ212418.93+855645 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.12                                KD                                                                                               
WDJ212418.93+855645 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.12                                G                                                                                                
WDJ212418.93+855645 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.12                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [102]

Visit: 1V (WDJ083637.32-281638.66)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ083637.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     2-281638.66          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ083637.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     2-281638.66          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ083637.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2-281638.66          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ083637.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2-281638.66          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ083637.32-281638 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.66                                KXD                                                                                              
WDJ083637.32-281638 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.66                                KD                                                                                               
WDJ083637.32-281638 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.66                                G                                                                                                
WDJ083637.32-281638 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.66                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [103]

Visit: 1W (WDJ090638.59+070059.81)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ090638.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     9+070059.81          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ090638.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     9+070059.81          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ090638.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9+070059.81          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ090638.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9+070059.81          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ090638.59+070059 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.81                                KXD                                                                                              
WDJ090638.59+070059 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.81                                KD                                                                                               
WDJ090638.59+070059 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.81                                G                                                                                                
WDJ090638.59+070059 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.81                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [104]

Visit: 1X (WDJ124752.77-412810.27)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ124752.7 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     7-412810.27          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ124752.7 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     7-412810.27          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ124752.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7-412810.27          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ124752.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7-412810.27          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ124752.77-412810 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.27                                KXD                                                                                              
WDJ124752.77-412810 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.27                                KD                                                                                               
WDJ124752.77-412810 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.27                                G                                                                                                
WDJ124752.77-412810 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.27                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [105]

Visit: 1Y (WDJ132230.90-061158.15)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ132230.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     0-061158.15          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ132230.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     0-061158.15          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ132230.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-061158.15          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ132230.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-061158.15          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ132230.90-061158 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                KXD                                                                                              
WDJ132230.90-061158 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                KD                                                                                               
WDJ132230.90-061158 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                G                                                                                                
WDJ132230.90-061158 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [106]

Visit: 1Z (WDJ211146.39+012054.26)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ211146.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     9+012054.26          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ211146.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     9+012054.26          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ211146.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9+012054.26          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ211146.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     9+012054.26          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ211146.39+012054 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.26                                KXD                                                                                              
WDJ211146.39+012054 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.26                                KD                                                                                               
WDJ211146.39+012054 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.26                                G                                                                                                
WDJ211146.39+012054 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.26                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [107]

Visit: 20 (WDJ142234.18-102408.81)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ142234.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     8-102408.81          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ142234.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     8-102408.81          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ142234.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=280, FLASH=YES,    1   390 S (390                          
     8-102408.81          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ142234.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=280, FLASH=YES,    1   390 S (390                          
     8-102408.81          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ142234.18-102408 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.81                                KXD                                                                                              
WDJ142234.18-102408 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.81                                KD                                                                                               
WDJ142234.18-102408 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.81                                G                                                                                                
WDJ142234.18-102408 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.81                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [108]

Visit: 21 (WDJ153037.04-355504.21)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ153037.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     4-355504.21          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ153037.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     4-355504.21          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ153037.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=180, FLASH=YES,    1   470 S (470                          
     4-355504.21          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ153037.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=180, FLASH=YES,    1   470 S (470                          
     4-355504.21          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ153037.04-355504 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KXD                                                                                              
WDJ153037.04-355504 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KD                                                                                               
WDJ153037.04-355504 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
WDJ153037.04-355504 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [109]

Visit: 22 (WDJ161523.98-111830.09)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ161523.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     8-111830.09          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ161523.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     8-111830.09          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ161523.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=500, FLASH=YES,    1   610 S (610                          
     8-111830.09          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ161523.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=500, FLASH=YES,    1   610 S (610                          
     8-111830.09          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ161523.98-111830 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.09                                KXD                                                                                              
WDJ161523.98-111830 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.09                                KD                                                                                               
WDJ161523.98-111830 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.09                                G                                                                                                
WDJ161523.98-111830 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.09                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [110]

Visit: 23 (WDJ170256.34-531436.57)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ170256.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     4-531436.57          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ170256.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     4-531436.57          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ170256.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=684, FLASH=YES,    1   794 S (794                          
     4-531436.57          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ170256.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=684, FLASH=YES,    1   794 S (794                          
     4-531436.57          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ170256.34-531436 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.57                                KXD                                                                                              
WDJ170256.34-531436 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.57                                KD                                                                                               
WDJ170256.34-531436 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.57                                G                                                                                                
WDJ170256.34-531436 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.57                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [111]

Visit: 25 (WDJ181854.22-475748.50)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ181854.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     2-475748.50          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ181854.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     2-475748.50          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ181854.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=122, FLASH=YES,    1   232 S (232                          
     2-475748.50          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ181854.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=122, FLASH=YES,    1   232 S (232                          
     2-475748.50          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ181854.22-475748 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.50                                KXD                                                                                              
WDJ181854.22-475748 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.50                                KD                                                                                               
WDJ181854.22-475748 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.50                                G                                                                                                
WDJ181854.22-475748 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.50                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [112]

Visit: 26 (WDJ184816.39-141522.33)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: This visit was never set to flight ready because of BOP concerns with the original target.  
                          We substituted the target from the failed visit 67 into it.                                 


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ184816.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     9-141522.33          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ184816.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     9-141522.33          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ184816.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=187, FLASH=YES,    1   484 S (484                          
     9-141522.33          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ184816.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=187, FLASH=YES,    1   484 S (484                          
     9-141522.33          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ184816.39-141522 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                KXD                                                                                              
WDJ184816.39-141522 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                KD                                                                                               
WDJ184816.39-141522 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                G                                                                                                
WDJ184816.39-141522 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [113]

Visit: 27 (WDJ194925.91-440512.18)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ194925.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     1-440512.18          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ194925.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     1-440512.18          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ194925.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=110, FLASH=YES,    1   220 S (220                          
     1-440512.18          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ194925.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=110, FLASH=YES,    1   220 S (220                          
     1-440512.18          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ194925.91-440512 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.18                                KXD                                                                                              
WDJ194925.91-440512 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.18                                KD                                                                                               
WDJ194925.91-440512 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.18                                G                                                                                                
WDJ194925.91-440512 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.18                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [114]

Visit: 28 (WDJ203210.13+215410.33)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ203210.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     3+215410.33          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ203210.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     3+215410.33          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ203210.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=135, FLASH=YES,    1   245 S (245                          
     3+215410.33          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ203210.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=135, FLASH=YES,    1   245 S (245                          
     3+215410.33          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ203210.13+215410 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                KXD                                                                                              
WDJ203210.13+215410 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                KD                                                                                               
WDJ203210.13+215410 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                G                                                                                                
WDJ203210.13+215410 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.33                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [115]

Visit: 29 (WDJ215453.40-302918.67)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ215453.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     0-302918.67          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ215453.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     0-302918.67          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ215453.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=143, FLASH=YES,    1   185 S (185                          
     0-302918.67          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ215453.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=143, FLASH=YES,    1   185 S (185                          
     0-302918.67          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ215453.40-302918 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.67                                KXD                                                                                              
WDJ215453.40-302918 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.67                                KD                                                                                               
WDJ215453.40-302918 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.67                                G                                                                                                
WDJ215453.40-302918 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.67                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [116]

Visit: 2A (WDJ085708.32-603245.24)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ085708.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     2-603245.24          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ085708.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     2-603245.24          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ085708.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2-603245.24          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ085708.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2-603245.24          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ085708.32-603245 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.24                                KXD                                                                                              
WDJ085708.32-603245 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.24                                KD                                                                                               
WDJ085708.32-603245 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.24                                G                                                                                                
WDJ085708.32-603245 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.24                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [117]

Visit: 2B (WDJ031743.17+090955.15)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ031743.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     7+090955.15          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ031743.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     7+090955.15          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ031743.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7+090955.15          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ031743.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7+090955.15          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ031743.17+090955 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                KXD                                                                                              
WDJ031743.17+090955 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                KD                                                                                               
WDJ031743.17+090955 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                G                                                                                                
WDJ031743.17+090955 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.15                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [118]

Visit: 2C (WDJ074735.98+210635.83)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ074735.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     8+210635.83          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ074735.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     8+210635.83          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ074735.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8+210635.83          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ074735.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8+210635.83          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ074735.98+210635 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                KXD                                                                                              
WDJ074735.98+210635 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                KD                                                                                               
WDJ074735.98+210635 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                G                                                                                                
WDJ074735.98+210635 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [119]

Visit: 30 (WDJ221153.92+564946.77)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ221153.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     2+564946.77          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ221153.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     2+564946.77          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ221153.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=195, FLASH=YES,    1   1000 S                              
     2+564946.77          G                                  FP-POS=3                           (1000 S)                            
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ221153.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=195, FLASH=YES,    1   1000 S                              
     2+564946.77          G                                  FP-POS=4                           (1000 S)                            
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ221153.92+564946 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                KXD                                                                                              
WDJ221153.92+564946 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                KD                                                                                               
WDJ221153.92+564946 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                G                                                                                                
WDJ221153.92+564946 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [120]

Visit: 31 (WDJ225510.55-631031.04)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ225510.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     5-631031.04          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ225510.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     5-631031.04          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ225510.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=195, FLASH=YES,    1   500 S (500                          
     5-631031.04          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ225510.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=195, FLASH=YES,    1   500 S (500                          
     5-631031.04          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ225510.55-631031 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.04                                KXD                                                                                              
WDJ225510.55-631031 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.04                                KD                                                                                               
WDJ225510.55-631031 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.04                                G                                                                                                
WDJ225510.55-631031 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.04                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [121]

Visit: 32 (WDJ232337.94+341526.71)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ232337.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     4+341526.71          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ232337.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     4+341526.71          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ232337.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=263, FLASH=YES,    1   900 S (900                          
     4+341526.71          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ232337.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=263, FLASH=YES,    1   900 S (900                          
     4+341526.71          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ232337.94+341526 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.71                                KXD                                                                                              
WDJ232337.94+341526 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.71                                KD                                                                                               
WDJ232337.94+341526 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.71                                G                                                                                                
WDJ232337.94+341526 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.71                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [122]

Visit: 33 (WDJ233738.74-411032.64)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ233738.7 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     4-411032.64          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ233738.7 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     4-411032.64          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ233738.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=263, FLASH=YES,    1   900 S (900                          
     4-411032.64          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ233738.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=263, FLASH=YES,    1   900 S (900                          
     4-411032.64          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ233738.74-411032 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.64                                KXD                                                                                              
WDJ233738.74-411032 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.64                                KD                                                                                               
WDJ233738.74-411032 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.64                                G                                                                                                
WDJ233738.74-411032 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.64                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [123]

Visit: 34 (WDJ234331.84-882310.21)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ234331.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     4-882310.21          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ234331.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     4-882310.21          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ234331.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=180, FLASH=YES,    1   290 S (290                          
     4-882310.21          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ234331.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=180, FLASH=YES,    1   290 S (290                          
     4-882310.21          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ234331.84-882310 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KXD                                                                                              
WDJ234331.84-882310 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KD                                                                                               
WDJ234331.84-882310 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
WDJ234331.84-882310 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [124]

Visit: 35 (WDJ234805.65+410215.96)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ234805.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     5+410215.96          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ234805.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     5+410215.96          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ234805.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=263, FLASH=YES,    1   900 S (900                          
     5+410215.96          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ234805.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=263, FLASH=YES,    1   900 S (900                          
     5+410215.96          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ234805.65+410215 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.96                                KXD                                                                                              
WDJ234805.65+410215 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.96                                KD                                                                                               
WDJ234805.65+410215 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.96                                G                                                                                                
WDJ234805.65+410215 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.96                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [125]

Visit: 36 (WDJ160317.23-192354.77)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ160317.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     3-192354.77          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ160317.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     3-192354.77          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ160317.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=163, FLASH=YES,    1   435 S (435                          
     3-192354.77          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ160317.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=163, FLASH=YES,    1   435 S (435                          
     3-192354.77          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ160317.23-192354 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                KXD                                                                                              
WDJ160317.23-192354 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                KD                                                                                               
WDJ160317.23-192354 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                G                                                                                                
WDJ160317.23-192354 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [126]

Visit: 37 (WDJ023016.63+051550.70)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ023016.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     3+051550.70          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ023016.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     3+051550.70          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ023016.6 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=3                       1   86 S (86                            
     3+051550.70                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ023016.6 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=4                       1   86 S (86                            
     3+051550.70                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ023016.63+051550 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                KXD                                                                                              
WDJ023016.63+051550 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                KD                                                                                               
WDJ023016.63+051550 3     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                                                                                                                 
WDJ023016.63+051550 4     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                                                                                                                 
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [127]

Visit: 38 (WDJ201056.85-301306.63)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ201056.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     5-301306.63          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ201056.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     5-301306.63          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ201056.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=195, FLASH=YES,    1   500 S (500                          
     5-301306.63          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ201056.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=195, FLASH=YES,    1   500 S (500                          
     5-301306.63          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ201056.85-301306 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                KXD                                                                                              
WDJ201056.85-301306 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                KD                                                                                               
WDJ201056.85-301306 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                G                                                                                                
WDJ201056.85-301306 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [128]

Visit: 39 (WDJ215225.38+022319.58)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ215225.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     8+022319.58          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ215225.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     8+022319.58          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ215225.3 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=3                       1   500 S (500                          
     8+022319.58                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ215225.3 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=4                       1   500 S (500                          
     8+022319.58                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ215225.38+022319 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.58                                KXD                                                                                              
WDJ215225.38+022319 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.58                                KD                                                                                               
WDJ215225.38+022319 3     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.58                                                                                                                                 
WDJ215225.38+022319 4     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.58                                                                                                                                 
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [129]

Visit: 40 (WDJ014128.80+833458.83)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ014128.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     0+833458.83          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ014128.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     0+833458.83          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ014128.8 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=3                       1   500 S (500                          
     0+833458.83                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ014128.8 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=4                       1   500 S (500                          
     0+833458.83                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ014128.80+833458 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                KXD                                                                                              
WDJ014128.80+833458 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                KD                                                                                               
WDJ014128.80+833458 3     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                                                                                                                 
WDJ014128.80+833458 4     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                                                                                                                 
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [130]

Visit: 41 (WDJ012923.99+510846.97)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ012923.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     9+510846.97          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ012923.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     9+510846.97          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ012923.9 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=3                       1   105 S (105                          
     9+510846.97                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ012923.9 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=4                       1   105 S (105                          
     9+510846.97                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ012923.99+510846 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                KXD                                                                                              
WDJ012923.99+510846 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                KD                                                                                               
WDJ012923.99+510846 3     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                                                                                                                 
WDJ012923.99+510846 4     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                                                                                                                 
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [131]

Visit: 42 (WDJ164718.39+322832.87)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ164718.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     9+322832.87          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ164718.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     9+322832.87          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ164718.3 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=3                       1   121 S (121                          
     9+322832.87                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ164718.3 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=4                       1   121 S (121                          
     9+322832.87                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ164718.39+322832 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.87                                KXD                                                                                              
WDJ164718.39+322832 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.87                                KD                                                                                               
WDJ164718.39+322832 3     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.87                                                                                                                                 
WDJ164718.39+322832 4     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.87                                                                                                                                 
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [132]

Visit: 43 (WDJ022827.20-324233.80)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ022827.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     0-324233.80          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ022827.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     0-324233.80          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ022827.2 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=3                       1   500 S (500                          
     0-324233.80                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ022827.2 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=4                       1   500 S (500                          
     0-324233.80                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ022827.20-324233 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                KXD                                                                                              
WDJ022827.20-324233 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                KD                                                                                               
WDJ022827.20-324233 3     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                                                                                                                 
WDJ022827.20-324233 4     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                                                                                                                 
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [133]

Visit: 44 (WDJ042839.41+165812.09)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ042839.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     1+165812.09          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ042839.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     1+165812.09          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ042839.4 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=3                       1   135 S (135                          
     1+165812.09                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ042839.4 COS/FUV  ACCUM   PSA       G130M    1291    FP-POS=4                       1   135 S (135                          
     1+165812.09                                                                                S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ042839.41+165812 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.09                                KXD                                                                                              
WDJ042839.41+165812 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.09                                KD                                                                                               
WDJ042839.41+165812 3     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.09                                                                                                                                 
WDJ042839.41+165812 4     COS/FUV  ACCUM   PSA      G130M    1291  none         none         none       none       1       N/A      
.09                                                                                                                                 
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [134]

Visit: 45 (WDJ213849.48-404127.74)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ213849.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     8-404127.74          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ213849.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     8-404127.74          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ213849.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=160, FLASH=YES,    1   160 S (160                          
     8-404127.74          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ213849.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=160, FLASH=YES,    1   160 S (160                          
     8-404127.74          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ213849.48-404127 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                KXD                                                                                              
WDJ213849.48-404127 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                KD                                                                                               
WDJ213849.48-404127 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                G                                                                                                
WDJ213849.48-404127 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.74                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [135]

Visit: 46 (WDJ005340.54+360118.17)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ005340.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     4+360118.17          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ005340.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     4+360118.17          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ005340.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=168, FLASH=YES,    1   614 S (614                          
     4+360118.17          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ005340.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=168, FLASH=YES,    1   614 S (614                          
     4+360118.17          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ005340.54+360118 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.17                                KXD                                                                                              
WDJ005340.54+360118 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.17                                KD                                                                                               
WDJ005340.54+360118 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.17                                G                                                                                                
WDJ005340.54+360118 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.17                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [136]

Visit: 47 (WDJ221153.92+564946.77 #2)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ221153.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     2+564946.77          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ221153.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     2+564946.77          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ221153.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=240, FLASH=YES,    1   350 S (350                          
     2+564946.77          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ221153.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=240, FLASH=YES,    1   350 S (350                          
     2+564946.77          G                                  FP-POS=4                           S)                                  
   Comments:  This is a repeat of the failed visit 30       
              (shutter closed), but updated for S/N=30      
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ221153.92+564946 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                KXD                                                                                              
WDJ221153.92+564946 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                KD                                                                                               
WDJ221153.92+564946 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                G                                                                                                
WDJ221153.92+564946 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [137]

Visit: 48 (WDJ020847.22+251409.97)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ020847.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     2+251409.97          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ020847.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     2+251409.97          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ020847.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=194, FLASH=YES,    1   194 S (194                          
     2+251409.97          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ020847.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=194, FLASH=YES,    1   194 S (194                          
     2+251409.97          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ020847.22+251409 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                KXD                                                                                              
WDJ020847.22+251409 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                KD                                                                                               
WDJ020847.22+251409 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                G                                                                                                
WDJ020847.22+251409 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [138]

Visit: 49 (WDJ002702.78-075111.86)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ002702.7 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     8-075111.86          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ002702.7 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     8-075111.86          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ002702.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=163, FLASH=YES,    1   182 S (182                          
     8-075111.86          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ002702.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=163, FLASH=YES,    1   182 S (182                          
     8-075111.86          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ002702.78-075111 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.86                                KXD                                                                                              
WDJ002702.78-075111 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.86                                KD                                                                                               
WDJ002702.78-075111 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.86                                G                                                                                                
WDJ002702.78-075111 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.86                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [139]

Visit: 50 (WDJ184225.24-780505.16 #2)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ184225.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     4-780505.16          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ184225.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     4-780505.16          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ184225.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-780505.16          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ184225.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-780505.16          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ184225.24-780505 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                KXD                                                                                              
WDJ184225.24-780505 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                KD                                                                                               
WDJ184225.24-780505 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                G                                                                                                
WDJ184225.24-780505 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.16                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [140]

Visit: 51 (WDJ041051.67+592503.39)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ041051.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     7+592503.39          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ041051.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     7+592503.39          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ041051.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=117, FLASH=YES,    1   460 S (460                          
     7+592503.39          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ041051.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=117, FLASH=YES,    1   460 S (460                          
     7+592503.39          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ041051.67+592503 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.39                                KXD                                                                                              
WDJ041051.67+592503 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.39                                KD                                                                                               
WDJ041051.67+592503 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.39                                G                                                                                                
WDJ041051.67+592503 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.39                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [141]

Visit: 52 (WDJ213611.14-260959.43)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ213611.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   0.5 S (0.5                          
     4-260959.43          KXD                                                                   S)                                  
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ213611.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   0.5 S (0.5                          
     4-260959.43          KD                                 CENTER=DEF                         S)                                  
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ213611.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=295, FLASH=YES,    1   700 S (700                          
     4-260959.43          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ213611.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=295, FLASH=YES,    1   700 S (700                          
     4-260959.43          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ213611.14-260959 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                KXD                                                                                              
WDJ213611.14-260959 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                KD                                                                                               
WDJ213611.14-260959 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                G                                                                                                
WDJ213611.14-260959 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [142]

Visit: 53 (WDJ213712.53+473459.98 #2)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ213712.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3+473459.98          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ213712.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3+473459.98          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ213712.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+473459.98          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ213712.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+473459.98          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ213712.53+473459 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                KXD                                                                                              
WDJ213712.53+473459 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                KD                                                                                               
WDJ213712.53+473459 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                G                                                                                                
WDJ213712.53+473459 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [143]

Visit: 54 (WDJ235200.03-033654.01 #2)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ235200.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3-033654.01          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ235200.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3-033654.01          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ235200.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-033654.01          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ235200.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-033654.01          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ235200.03-033654 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KXD                                                                                              
WDJ235200.03-033654 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KD                                                                                               
WDJ235200.03-033654 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
WDJ235200.03-033654 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [144]

Visit: 55 (WDJ084041.95+553958.80)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ084041.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     5+553958.80          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ084041.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     5+553958.80          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ084041.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=530, FLASH=YES,    1   640 S (640                          
     5+553958.80          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ084041.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=530, FLASH=YES,    1   640 S (640                          
     5+553958.80          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ084041.95+553958 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                KXD                                                                                              
WDJ084041.95+553958 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                KD                                                                                               
WDJ084041.95+553958 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                G                                                                                                
WDJ084041.95+553958 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [145]

Visit: 56 (WDJ080710.46-362251.69)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ080710.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     6-362251.69          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ080710.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     6-362251.69          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ080710.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=561, FLASH=YES,    1   671 S (671                          
     6-362251.69          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ080710.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=561, FLASH=YES,    1   671 S (671                          
     6-362251.69          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ080710.46-362251 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.69                                KXD                                                                                              
WDJ080710.46-362251 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.69                                KD                                                                                               
WDJ080710.46-362251 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.69                                G                                                                                                
WDJ080710.46-362251 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.69                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [146]

Visit: 57 (WDJ034306.45+320139.89)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ034306.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     5+320139.89          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ034306.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     5+320139.89          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ034306.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   875 S (875                          
     5+320139.89          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ034306.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   875 S (875                          
     5+320139.89          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ034306.45+320139 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.89                                KXD                                                                                              
WDJ034306.45+320139 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.89                                KD                                                                                               
WDJ034306.45+320139 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.89                                G                                                                                                
WDJ034306.45+320139 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.89                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [147]

Visit: 58 (WDJ085628.48+653946.01 #2)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ085628.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     8+653946.01          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ085628.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     8+653946.01          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ085628.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8+653946.01          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ085628.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8+653946.01          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ085628.48+653946 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KXD                                                                                              
WDJ085628.48+653946 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KD                                                                                               
WDJ085628.48+653946 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
WDJ085628.48+653946 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [148]

Visit: 60 (WDJ080016.15+004045.91)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ080016.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     5+004045.91          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ080016.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     5+004045.91          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ080016.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     5+004045.91          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ080016.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     5+004045.91          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ080016.15+004045 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.91                                KXD                                                                                              
WDJ080016.15+004045 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.91                                KD                                                                                               
WDJ080016.15+004045 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.91                                G                                                                                                
WDJ080016.15+004045 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.91                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [149]

Visit: 61 (WDJ193505.26-173953.55)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ193505.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     6-173953.55          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ193505.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     6-173953.55          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ193505.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-173953.55          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ193505.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-173953.55          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ193505.26-173953 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.55                                KXD                                                                                              
WDJ193505.26-173953 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.55                                KD                                                                                               
WDJ193505.26-173953 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.55                                G                                                                                                
WDJ193505.26-173953 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.55                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [150]

Visit: 62 (WDJ093538.07-585600.61)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ093538.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     7-585600.61          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ093538.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     7-585600.61          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ093538.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7-585600.61          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ093538.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7-585600.61          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ093538.07-585600 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.61                                KXD                                                                                              
WDJ093538.07-585600 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.61                                KD                                                                                               
WDJ093538.07-585600 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.61                                G                                                                                                
WDJ093538.07-585600 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.61                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [151]

Visit: 63 (WDJ103349.20+230916.26)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ103349.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     0+230916.26          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ103349.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     0+230916.26          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ103349.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0+230916.26          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ103349.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0+230916.26          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ103349.20+230916 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.26                                KXD                                                                                              
WDJ103349.20+230916 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.26                                KD                                                                                               
WDJ103349.20+230916 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.26                                G                                                                                                
WDJ103349.20+230916 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.26                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [152]

Visit: 64 (WDJ154100.93-362214.98)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ154100.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     3-362214.98          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ154100.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     3-362214.98          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ154100.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-362214.98          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ154100.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-362214.98          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ154100.93-362214 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                KXD                                                                                              
WDJ154100.93-362214 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                KD                                                                                               
WDJ154100.93-362214 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                G                                                                                                
WDJ154100.93-362214 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.98                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [153]

Visit: 65 (WDJ010419.33+381655.23)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ010419.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     3+381655.23          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ010419.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     3+381655.23          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ010419.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+381655.23          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ010419.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3+381655.23          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ010419.33+381655 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                KXD                                                                                              
WDJ010419.33+381655 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                KD                                                                                               
WDJ010419.33+381655 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                G                                                                                                
WDJ010419.33+381655 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [154]

Visit: 66 (WDJ201719.80-074819.01)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ201719.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   2 S (2 S)                           
     0-074819.01          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ201719.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   2 S (2 S)                           
     0-074819.01          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ201719.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-074819.01          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ201719.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-074819.01          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ201719.80-074819 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KXD                                                                                              
WDJ201719.80-074819 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KD                                                                                               
WDJ201719.80-074819 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
WDJ201719.80-074819 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [155]

Visit: 67 (WDJ030350.56+060748.75)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ030350.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     6+060748.75          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ030350.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     6+060748.75          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ030350.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6+060748.75          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ030350.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6+060748.75          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ030350.56+060748 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                KXD                                                                                              
WDJ030350.56+060748 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                KD                                                                                               
WDJ030350.56+060748 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                G                                                                                                
WDJ030350.56+060748 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.75                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [156]

Visit: 68 (WDJ191850.20+333602.29)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ191850.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     0+333602.29          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ191850.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     0+333602.29          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ191850.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0+333602.29          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ191850.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0+333602.29          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ191850.20+333602 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.29                                KXD                                                                                              
WDJ191850.20+333602 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.29                                KD                                                                                               
WDJ191850.20+333602 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.29                                G                                                                                                
WDJ191850.20+333602 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.29                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [157]

Visit: 69 (WDJ052658.86-702617.08)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ052658.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     6-702617.08          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ052658.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     6-702617.08          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ052658.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-702617.08          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ052658.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-702617.08          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ052658.86-702617 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                KXD                                                                                              
WDJ052658.86-702617 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                KD                                                                                               
WDJ052658.86-702617 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                G                                                                                                
WDJ052658.86-702617 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.08                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [158]

Visit: 70 (WDJ145333.03-304023.77)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ145333.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     3-304023.77          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ145333.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     3-304023.77          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ145333.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-304023.77          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ145333.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-304023.77          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ145333.03-304023 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                KXD                                                                                              
WDJ145333.03-304023 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                KD                                                                                               
WDJ145333.03-304023 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                G                                                                                                
WDJ145333.03-304023 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.77                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [159]

Visit: 71 (WDJ073739.33-294456.83)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ073739.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     3-294456.83          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ073739.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     3-294456.83          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ073739.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-294456.83          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ073739.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-294456.83          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ073739.33-294456 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                KXD                                                                                              
WDJ073739.33-294456 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                KD                                                                                               
WDJ073739.33-294456 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                G                                                                                                
WDJ073739.33-294456 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.83                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [160]

Visit: 72 (WDJ154754.64-432801.53)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ154754.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     4-432801.53          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ154754.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     4-432801.53          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ154754.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-432801.53          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ154754.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-432801.53          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ154754.64-432801 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.53                                KXD                                                                                              
WDJ154754.64-432801 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.53                                KD                                                                                               
WDJ154754.64-432801 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.53                                G                                                                                                
WDJ154754.64-432801 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.53                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [161]

Visit: 73 (WDJ192000.84-224152.97)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ192000.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     4-224152.97          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ192000.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     4-224152.97          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ192000.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-224152.97          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ192000.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-224152.97          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ192000.84-224152 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                KXD                                                                                              
WDJ192000.84-224152 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                KD                                                                                               
WDJ192000.84-224152 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                G                                                                                                
WDJ192000.84-224152 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.97                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [162]

Visit: 74 (WDJ043704.01-572821.62)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ043704.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     1-572821.62          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ043704.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     1-572821.62          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ043704.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-572821.62          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ043704.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-572821.62          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ043704.01-572821 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.62                                KXD                                                                                              
WDJ043704.01-572821 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.62                                KD                                                                                               
WDJ043704.01-572821 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.62                                G                                                                                                
WDJ043704.01-572821 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.62                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [163]

Visit: 75 (WDJ205538.86-174004.87)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ205538.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     6-174004.87          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ205538.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     6-174004.87          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ205538.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-174004.87          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ205538.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-174004.87          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ205538.86-174004 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.87                                KXD                                                                                              
WDJ205538.86-174004 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.87                                KD                                                                                               
WDJ205538.86-174004 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.87                                G                                                                                                
WDJ205538.86-174004 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.87                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [164]

Visit: 76 (WDJ080132.70-060735.48)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ080132.7 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     0-060735.48          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ080132.7 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     0-060735.48          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ080132.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-060735.48          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ080132.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-060735.48          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ080132.70-060735 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.48                                KXD                                                                                              
WDJ080132.70-060735 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.48                                KD                                                                                               
WDJ080132.70-060735 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.48                                G                                                                                                
WDJ080132.70-060735 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.48                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [165]

Visit: 77 (WDJ200946.56-772116.06)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ200946.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     6-772116.06          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ200946.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     6-772116.06          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ200946.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-772116.06          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ200946.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-772116.06          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ200946.56-772116 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                KXD                                                                                              
WDJ200946.56-772116 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                KD                                                                                               
WDJ200946.56-772116 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                G                                                                                                
WDJ200946.56-772116 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.06                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [166]

Visit: 78 (WDJ085628.48+653946.01)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ085628.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     8+653946.01          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ085628.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     8+653946.01          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ085628.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8+653946.01          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ085628.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8+653946.01          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ085628.48+653946 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KXD                                                                                              
WDJ085628.48+653946 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                KD                                                                                               
WDJ085628.48+653946 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
WDJ085628.48+653946 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.01                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [167]

Visit: 79 (WDJ052137.30-111434.43)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ052137.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     0-111434.43          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ052137.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     0-111434.43          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ052137.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-111434.43          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ052137.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-111434.43          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ052137.30-111434 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                KXD                                                                                              
WDJ052137.30-111434 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                KD                                                                                               
WDJ052137.30-111434 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                G                                                                                                
WDJ052137.30-111434 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [168]

Visit: 80 (WDJ222734.23-601142.21)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ222734.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     3-601142.21          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ222734.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     3-601142.21          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ222734.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-601142.21          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ222734.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-601142.21          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ222734.23-601142 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KXD                                                                                              
WDJ222734.23-601142 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KD                                                                                               
WDJ222734.23-601142 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
WDJ222734.23-601142 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [169]

Visit: 81 (WDJ122448.14+792042.55)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ122448.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     4+792042.55          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ122448.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     4+792042.55          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ122448.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4+792042.55          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ122448.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4+792042.55          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ122448.14+792042 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.55                                KXD                                                                                              
WDJ122448.14+792042 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.55                                KD                                                                                               
WDJ122448.14+792042 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.55                                G                                                                                                
WDJ122448.14+792042 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.55                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [170]

Visit: 82 (WDJ181348.56+211920.66)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ181348.5 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     6+211920.66          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ181348.5 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     6+211920.66          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ181348.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6+211920.66          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ181348.5 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6+211920.66          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ181348.56+211920 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.66                                KXD                                                                                              
WDJ181348.56+211920 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.66                                KD                                                                                               
WDJ181348.56+211920 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.66                                G                                                                                                
WDJ181348.56+211920 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.66                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [171]

Visit: 83 (WDJ022340.37+481647.23)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ022340.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     7+481647.23          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ022340.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     7+481647.23          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ022340.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7+481647.23          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ022340.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     7+481647.23          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ022340.37+481647 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                KXD                                                                                              
WDJ022340.37+481647 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                KD                                                                                               
WDJ022340.37+481647 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                G                                                                                                
WDJ022340.37+481647 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [172]

Visit: 84 (WDJ150040.16-370338.80)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ150040.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     6-370338.80          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ150040.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     6-370338.80          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ150040.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-370338.80          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ150040.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-370338.80          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ150040.16-370338 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                KXD                                                                                              
WDJ150040.16-370338 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                KD                                                                                               
WDJ150040.16-370338 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                G                                                                                                
WDJ150040.16-370338 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.80                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [173]

Visit: 85 (WDJ084215.02-022226.79)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ084215.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   3 S (3 S)                           
     2-022226.79          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ084215.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   3 S (3 S)                           
     2-022226.79          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ084215.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2-022226.79          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ084215.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     2-022226.79          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ084215.02-022226 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.79                                KXD                                                                                              
WDJ084215.02-022226 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.79                                KD                                                                                               
WDJ084215.02-022226 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.79                                G                                                                                                
WDJ084215.02-022226 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.79                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [174]

Visit: 86 (WDJ025251.00-022517.99)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ025251.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     0-022517.99          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ025251.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     0-022517.99          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ025251.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-022517.99          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ025251.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-022517.99          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ025251.00-022517 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                KXD                                                                                              
WDJ025251.00-022517 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                KD                                                                                               
WDJ025251.00-022517 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                G                                                                                                
WDJ025251.00-022517 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [175]

Visit: 87 (WDJ201900.44+401649.99)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ201900.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     4+401649.99          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ201900.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     4+401649.99          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ201900.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4+401649.99          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ201900.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4+401649.99          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ201900.44+401649 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                KXD                                                                                              
WDJ201900.44+401649 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                KD                                                                                               
WDJ201900.44+401649 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                G                                                                                                
WDJ201900.44+401649 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.99                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [176]

Visit: 88 (WDJ133110.86+340841.43)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ133110.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     6+340841.43          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ133110.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     6+340841.43          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ133110.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6+340841.43          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ133110.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6+340841.43          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ133110.86+340841 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                KXD                                                                                              
WDJ133110.86+340841 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                KD                                                                                               
WDJ133110.86+340841 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                G                                                                                                
WDJ133110.86+340841 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.43                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [177]

Visit: 89 (WDJ023802.20+221112.94)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ023802.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     0+221112.94          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ023802.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     0+221112.94          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ023802.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0+221112.94          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ023802.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0+221112.94          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ023802.20+221112 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.94                                KXD                                                                                              
WDJ023802.20+221112 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.94                                KD                                                                                               
WDJ023802.20+221112 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.94                                G                                                                                                
WDJ023802.20+221112 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.94                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [178]

Visit: 90 (WDJ120647.61-323433.11)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ120647.6 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     1-323433.11          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ120647.6 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     1-323433.11          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ120647.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-323433.11          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ120647.6 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-323433.11          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ120647.61-323433 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.11                                KXD                                                                                              
WDJ120647.61-323433 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.11                                KD                                                                                               
WDJ120647.61-323433 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.11                                G                                                                                                
WDJ120647.61-323433 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.11                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [179]

Visit: 91 (WDJ111658.44-163754.10)
     Visit Requirements:  ON HOLD                                                                                     
     On Hold Comments:    Needs BOP checking for the red companion.                                                   
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ111658.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     4-163754.10          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ111658.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     4-163754.10          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ111658.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-163754.10          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ111658.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     4-163754.10          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ111658.44-163754 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.10                                KXD                                                                                              
WDJ111658.44-163754 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.10                                KD                                                                                               
WDJ111658.44-163754 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.10                                G                                                                                                
WDJ111658.44-163754 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.10                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [180]

Visit: 92 (WDJ130130.71-723447.50)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ130130.7 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     1-723447.50          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ130130.7 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     1-723447.50          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ130130.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-723447.50          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ130130.7 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1-723447.50          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ130130.71-723447 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.50                                KXD                                                                                              
WDJ130130.71-723447 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.50                                KD                                                                                               
WDJ130130.71-723447 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.50                                G                                                                                                
WDJ130130.71-723447 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.50                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [181]

Visit: 93 (WDJ223531.08-571626.63)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ223531.0 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     8-571626.63          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ223531.0 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     8-571626.63          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ223531.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8-571626.63          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ223531.0 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8-571626.63          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ223531.08-571626 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                KXD                                                                                              
WDJ223531.08-571626 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                KD                                                                                               
WDJ223531.08-571626 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                G                                                                                                
WDJ223531.08-571626 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.63                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [182]

Visit: 94 (WDJ083523.43-435958.23)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ083523.4 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     3-435958.23          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ083523.4 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     3-435958.23          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ083523.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-435958.23          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ083523.4 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     3-435958.23          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ083523.43-435958 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                KXD                                                                                              
WDJ083523.43-435958 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                KD                                                                                               
WDJ083523.43-435958 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                G                                                                                                
WDJ083523.43-435958 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.23                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [183]

Visit: 95 (WDJ002001.81+135247.96)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ002001.8 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     1+135247.96          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ002001.8 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     1+135247.96          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ002001.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1+135247.96          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ002001.8 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     1+135247.96          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ002001.81+135247 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.96                                KXD                                                                                              
WDJ002001.81+135247 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.96                                KD                                                                                               
WDJ002001.81+135247 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.96                                G                                                                                                
WDJ002001.81+135247 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.96                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [184]

Visit: 96 (WDJ223621.10-195224.21)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ223621.1 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     0-195224.21          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ223621.1 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     0-195224.21          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ223621.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-195224.21          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ223621.1 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-195224.21          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ223621.10-195224 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KXD                                                                                              
WDJ223621.10-195224 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                KD                                                                                               
WDJ223621.10-195224 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
WDJ223621.10-195224 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.21                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [185]

Visit: 97 (WDJ231459.20-220821.70)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ231459.2 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     0-220821.70          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ231459.2 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     0-220821.70          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ231459.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-220821.70          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ231459.2 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     0-220821.70          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ231459.20-220821 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                KXD                                                                                              
WDJ231459.20-220821 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                KD                                                                                               
WDJ231459.20-220821 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                G                                                                                                
WDJ231459.20-220821 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.70                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [186]

Visit: 98 (WDJ170900.98-510117.25)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ170900.9 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     8-510117.25          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ170900.9 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     8-510117.25          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ170900.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8-510117.25          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ170900.9 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     8-510117.25          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ170900.98-510117 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.25                                KXD                                                                                              
WDJ170900.98-510117 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.25                                KD                                                                                               
WDJ170900.98-510117 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.25                                G                                                                                                
WDJ170900.98-510117 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.25                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [187]

Visit: 99 (WDJ152738.36-450207.41)
     Visit Requirements:  <none>                                                                                      
     On Hold Comments:    <none>                                                                                      
     Additional Comments: <none>                                                                                      


Exposures
------------------------------------------------------------------------------------------------------------------------------------
Exp |   Target  | Instr  | Oper. | Aper    |Spectral|Central|           Optional           |Num|   Time   |       Special
Num |    Name   | Config | Mode  | or FOV  |Element |Waveln.|          Parameters          |Exp|  (Total) |     Requirements
------------------------------------------------------------------------------------------------------------------------------------
1    WDJ152738.3 COS/FUV  ACQ/PEA PSA       G130M    1291                                   1   4 S (4 S)                           
     6-450207.41          KXD                                                                                                       
------------------------------------------------------------------------------------------------------------------------------------
2    WDJ152738.3 COS/FUV  ACQ/PEA PSA       G130M    1291    STEP-SIZE=0.9, NUM-POS=5,      1   4 S (4 S)                           
     6-450207.41          KD                                 CENTER=DEF                                                             
------------------------------------------------------------------------------------------------------------------------------------
3    WDJ152738.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-450207.41          G                                  FP-POS=3                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------
4    WDJ152738.3 COS/FUV  TIME-TA PSA       G130M    1291    BUFFER-TIME=395, FLASH=YES,    1   900 S (900                          
     6-450207.41          G                                  FP-POS=4                           S)                                  
------------------------------------------------------------------------------------------------------------------------------------

Sub Exposures
------------------------------------------------------------------------------------------------------------------------------------
Target             | Exp |Instr   | Oper. |  Aper  |Spectral|Cent.|Primary     |Secondary   |Iteration |CR-SPLIT  |Orbit  |Duration
Name               | Num |Config  | Mode  | or FOV |Element |Wave.|Pattern Pos |Pattern Pos |Num       |Num       |Number |
------------------------------------------------------------------------------------------------------------------------------------
WDJ152738.36-450207 1     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.41                                KXD                                                                                              
WDJ152738.36-450207 2     COS/FUV  ACQ/PEA PSA      G130M    1291  none         none         none       none       1       N/A      
.41                                KD                                                                                               
WDJ152738.36-450207 3     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.41                                G                                                                                                
WDJ152738.36-450207 4     COS/FUV  TIME-TA PSA      G130M    1291  none         none         none       none       1       N/A      
.41                                G                                                                                                
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [188]

            Summary Form for Proposal  17420

  Item                         Used in this proposal                                                                              
------------------------------------------------------------------------------------------------------------------------------------
  Apertures                    PSA                                                                                                 
------------------------------------------------------------------------------------------------------------------------------------
  Configurations               COS/FUV                                                                                             
------------------------------------------------------------------------------------------------------------------------------------
  Opmodes                      ACCUM, ACQ/PEAKD, ACQ/PEAKXD, TIME-TAG                                                              
------------------------------------------------------------------------------------------------------------------------------------
  Optional Parameters          BUFFER-TIME=110, BUFFER-TIME=117, BUFFER-TIME=122, BUFFER-TIME=130, BUFFER-TIME=135,                
                               BUFFER-TIME=143, BUFFER-TIME=160, BUFFER-TIME=163, BUFFER-TIME=168, BUFFER-TIME=180,                
                               BUFFER-TIME=187, BUFFER-TIME=194, BUFFER-TIME=195, BUFFER-TIME=240, BUFFER-TIME=245,                
                               BUFFER-TIME=263, BUFFER-TIME=280, BUFFER-TIME=281, BUFFER-TIME=295, BUFFER-TIME=334,                
                               BUFFER-TIME=350, BUFFER-TIME=395, BUFFER-TIME=415, BUFFER-TIME=430, BUFFER-TIME=460,                
                               BUFFER-TIME=500, BUFFER-TIME=520, BUFFER-TIME=530, BUFFER-TIME=561, BUFFER-TIME=625,                
                               BUFFER-TIME=645, BUFFER-TIME=665, BUFFER-TIME=684, BUFFER-TIME=790, CENTER=DEF, FLASH=YES,          
                               FP-POS=3, FP-POS=4, NUM-POS=5, STEP-SIZE=0.9                                                        
------------------------------------------------------------------------------------------------------------------------------------
  Special Requirements         ON HOLD                                                                                             
------------------------------------------------------------------------------------------------------------------------------------
  Spectral Elements            G130M                                                                                               
------------------------------------------------------------------------------------------------------------------------------------
                                                  17420( 13) - 10-Sep-2024 15:52:25 - [189]

  Target Names                 WDJ000538.55-600031.75, WDJ001717.99-192013.05, WDJ002001.81+135247.96, WDJ002702.78-075111.86,     
                               WDJ002959.00+364834.86, WDJ003340.89+555145.28, WDJ005340.54+360118.17, WDJ010419.33+381655.23,     
                               WDJ012923.99+510846.97, WDJ013139.22-201958.63, WDJ014128.80+833458.83, WDJ020847.22+251409.97,     
                               WDJ022340.37+481647.23, WDJ022827.20-324233.80, WDJ023016.63+051550.70, WDJ023802.20+221112.94,     
                               WDJ025251.00-022517.99, WDJ030350.56+060748.75, WDJ031715.85-853225.56, WDJ031719.13-853231.29,     
                               WDJ031743.17+090955.15, WDJ034306.45+320139.89, WDJ040223.78+320153.80, WDJ040607.08+543132.19,     
                               WDJ041051.67+592503.39, WDJ042839.41+165812.09, WDJ042842.36-100448.40, WDJ043659.47+253547.49,     
                               WDJ043704.01-572821.62, WDJ044759.97+554609.21, WDJ050940.99+015308.63, WDJ051613.96-701934.93,     
                               WDJ052137.30-111434.43, WDJ052658.86-702617.08, WDJ053343.43-271350.08, WDJ060308.63+451828.83,     
                               WDJ062117.23+370023.14, WDJ073504.07-794410.69, WDJ073739.33-294456.83, WDJ074735.98+210635.83,     
                               WDJ080016.15+004045.91, WDJ080132.70-060735.48, WDJ080710.46-362251.69, WDJ082246.16+361412.61,     
                               WDJ083152.65-261207.15, WDJ083523.43-435958.23, WDJ083637.32-281638.66, WDJ084041.95+553958.80,     
                               WDJ084215.02-022226.79, WDJ084747.35-731249.75, WDJ085047.51+172602.06, WDJ085628.48+653946.01,     
                               WDJ085708.32-603245.24, WDJ090515.08-234257.31, WDJ090638.59+070059.81, WDJ092008.26-400400.80,     
                               WDJ092224.63-314137.16, WDJ093538.07-585600.61, WDJ100337.51-451553.74, WDJ100551.52-023417.93,     
                               WDJ101420.66-041721.08, WDJ101511.71-010416.24, WDJ102228.77+124159.40, WDJ102846.64-214106.70,     
                               WDJ103349.20+230916.26, WDJ104346.70-390637.35, WDJ111658.44-163754.10, WDJ113842.69-584424.06,     
                               WDJ120347.43-002310.94, WDJ120647.61-323433.11, WDJ122448.14+792042.55, WDJ123213.30-040925.74,     
                               WDJ123226.19+412919.33, WDJ124752.77-412810.27, WDJ130130.71-723447.50, WDJ132230.90-061158.15,     
                               WDJ133110.86+340841.43, WDJ133913.54+120831.23, WDJ133915.05-370620.16, WDJ141651.40-705932.04,     
                               WDJ142234.18-102408.81, WDJ143526.31-055027.99, WDJ145333.03-304023.77, WDJ150040.16-370338.80,     
                               WDJ151103.63+765348.60, WDJ152131.86+381246.36, WDJ152738.36-450207.41, WDJ153037.04-355504.21,     
                               WDJ154100.93-362214.98, WDJ154754.64-432801.53, WDJ160317.23-192354.77, WDJ161523.98-111830.09,     
                               WDJ162044.87-190133.35, WDJ164718.39+322832.87, WDJ170120.99-191527.57, WDJ170256.34-531436.57,     
                               WDJ170900.98-510117.25, WDJ180228.51+005918.54, WDJ181348.56+211920.66, WDJ181854.22-475748.50,     
                               WDJ182227.62+532331.99, WDJ184225.24-780505.16, WDJ184816.39-141522.33, WDJ191850.20+333602.29,     
                               WDJ192000.84-224152.97, WDJ193505.26-173953.55, WDJ194925.91-440512.18, WDJ200823.87-660437.71,     
                               WDJ200946.56-772116.06, WDJ201056.85-301306.63, WDJ201501.62-565007.53, WDJ201719.80-074819.01,     
                               WDJ201900.44+401649.99, WDJ203210.13+215410.33, WDJ203645.86-251440.75, WDJ205109.94-753824.15,     
                               WDJ205525.69-225720.39, WDJ205538.86-174004.87, WDJ210428.02-031344.84, WDJ211146.39+012054.26,     
                               WDJ212418.93+855645.12, WDJ213333.32+352925.65, WDJ213611.14-260959.43, WDJ213712.53+473459.98,     
                               WDJ213849.48-404127.74, WDJ215225.38+022319.58, WDJ215453.40-302918.67, WDJ220113.96-220714.92,     
                               WDJ221153.92+564946.77, WDJ222734.23-601142.21, WDJ223531.08-571626.63, WDJ223621.10-195224.21,     
                               WDJ225510.55-631031.04, WDJ231459.20-220821.70, WDJ232337.94+341526.71, WDJ233738.74-411032.64,     
                               WDJ234331.84-882310.21, WDJ234805.65+410215.96, WDJ235200.03-033654.01, WDJ235223.18-280316.01,     
                               WDJ235857.81-445713.44                                                                              
------------------------------------------------------------------------------------------------------------------------------------

