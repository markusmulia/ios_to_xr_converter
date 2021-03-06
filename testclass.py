from ciscoconfparse import CiscoConfParse#Function check ios
class IosVrfConfigParser:
 #from ciscoconfparse import CiscoConfParse#Function check ios
 'Common base function for all vrf utility'

 @staticmethod    
 def ios_vrf_default_attrib():
  return {'VRF_NAME':'','RD':'','RT_EXPORT':[],'RT_IMPORT':[],'EX_MAP':[],'IM_MAP':[]}
  
 #check conf_file has vrf config
 @staticmethod
 def ios_has_vrf(conf_file):
  if not CiscoConfParse(conf_file).find_parents_w_child("^ip\svrf\s","rd"):
   return False 
  return True
  
 #function get list of vrf on conf_file
 @staticmethod
 def ios_get_list_vrf(conf_file):
  def_list = []
  if IosVrfConfigParser.ios_has_vrf(conf_file):
   return {x.replace('ip vrf ', '')for x in CiscoConfParse(conf_file).find_parents_w_child("^ip vrf ", "rd")}
  return []

 #function get number of configured vrf in conf_file
 @staticmethod
 def ios_get_vrf_count(conf_file):
  return len(IosVrfConfigParser.ios_get_list_vrf(conf_file))   
  
 #function get specific "vrf_name" configuration
 @staticmethod
 def ios_get_vrf_attrib(conf_file,vrf_name):
  #return CiscoConfParse(conf_file).find_all_children("ip vrf " + vrf_name)
  buff_vrf_attrib = IosVrfConfigParser.ios_vrf_default_attrib()
  buff = CiscoConfParse(CiscoConfParse(conf_file).find_all_children("ip vrf "+vrf_name), factory=True)
  obj = buff.find_objects('ip vrf ')[0]
  #print obj.ioscfg
  #save vrf name from arg
  buff_vrf_attrib['VRF_NAME'] = vrf_name
  #check rd if rd configured save rd
  if CiscoConfParse(obj.ioscfg).find_objects('rd'):
   buff_vrf_attrib['RD'] = str(CiscoConfParse(obj.ioscfg).find_objects(r'rd')[0].ioscfg).strip("'[]'").strip().replace('rd ','')
  #check export-map if configured save export-map
  if CiscoConfParse(obj.ioscfg).find_objects('export\smap'):
   #print "ada ex map"
   for x in CiscoConfParse(obj.ioscfg).find_objects('export\smap'):
    #print x.ioscfg
    buff_vrf_attrib['EX_MAP'].append(str(x.ioscfg).strip("'[]'").strip().replace('export map ',''))
   #check import-map if configured save import-map
  if CiscoConfParse(obj.ioscfg).find_objects('import\smap'):
   #print "ada imp map"
   for x in CiscoConfParse(obj.ioscfg).find_objects('import\smap'):
    #print x.ioscfg
    buff_vrf_attrib['IM_MAP'].append(str(x.ioscfg).strip("'[]'").strip().replace('import map ',''))
  if CiscoConfParse(obj.ioscfg).find_objects('route-target\sexport'):
   #print "route-target"
   for x in CiscoConfParse(obj.ioscfg).find_objects('route-target\sexport'):
    #print x.ioscfg
    buff_vrf_attrib['RT_EXPORT'].append(str(x.ioscfg).strip("'[]'").strip().replace('route-target export ',''))
  if CiscoConfParse(obj.ioscfg).find_objects('route-target\simport'):
     #print "route-target"
     for x in CiscoConfParse(obj.ioscfg).find_objects('route-target\simport'):
      #print x.ioscfg
      buff_vrf_attrib['RT_IMPORT'].append(str(x.ioscfg).strip("'[]'").strip().replace('route-target import ',''))	
  return buff_vrf_attrib
  
 @staticmethod
 def ios_get_all_vrf_attrib(conf_file):
  conf_buffer = []
  i = 0
  for vrf_name in IosVrfConfigParser.ios_get_list_vrf(conf_file):
   conf_buffer.append(IosVrfConfigParser.ios_get_vrf_attrib(conf_file,vrf_name))
  return conf_buffer

   
class IosToXRConverter:
 #procedure to convert specific vrf_name in conf_file form ios to ios-xr
 @staticmethod
 def convert_vrf(ios_conf_file,new_conf_file,vrf_name):
  xr_conf =  CiscoConfParse(new_conf_file) 
  vrf_attrib = IosVrfConfigParser.ios_get_vrf_attrib(ios_conf_file,vrf_name)
  
  if vrf_attrib['VRF_NAME']:
   print "create vrf config"
   xr_conf.append_line("vrf "+vrf_attrib['VRF_NAME'])
   xr_conf.append_line(" address-family ipv4 unicast")
  
  if vrf_attrib['EX_MAP']:
   print "create EXPORT Route-policy"
   for ex_map in vrf_attrib['EX_MAP']: 
    xr_conf.append_line(" export route-policy "+ex_map)
  
  if vrf_attrib['IM_MAP']:
   print "create IMPORT Route-policy"
   for im_map in vrf_attrib['IM_MAP']: 
    xr_conf.append_line(" export route-policy "+im_map)
	
  if vrf_attrib['RT_EXPORT']:
     print "create Export Route-Target "
     for rt_export in vrf_attrib['RT_EXPORT']: 
      xr_conf.append_line(" export route-target "+rt_export)

  if vrf_attrib['RT_IMPORT']:
     print "create Import Route-Target "
     for rt_import in vrf_attrib['RT_IMPORT']: 
      xr_conf.append_line(" export route-target "+rt_import)	
  xr_conf.commit()
  xr_conf.save_as(new_conf_file)
 
 @staticmethod
 #procedure to convert all configured vrf in conf_file from ios to ios-xr 
 def convert_all_vrf(ios_conf_file,new_conf_file):
  for vrf_name in IosVrfConfigParser.ios_get_list_vrf(ios_conf_file):
   print "create config for vrf"+vrf_name
   IosToXRConverter.convert_vrf(ios_conf_file,new_conf_file,vrf_name)

#for x in IosVrfConfigParser.ios_get_list_vrf("before_vrf.txt"):
# print x


#print IosVrfConfigParser.ios_get_vrf_config("before_vrf.txt","AIRASIA")

#IosVrfConfigParser.ios_get_all_vrf_config("before_vrf.txt")


#print "num of vrf"
#print IosVrfConfigParser.ios_get_vrf_count("before_vrf.txt")

#print len(IosVrfConfigParser.ios_get_all_vrf_config("before_vrf.txt"))

#IosToXRCoverter.convert_vrf("before.txt","newconfig.txt","AIRASIA")
IosToXRConverter.convert_all_vrf("before.txt","newconfig.txt")
