##############################################
#
#  60_freeairconnect.pm
#
#  2020 amenomade
#
#  This module reads and controls bluMartin freeair-connect airflow systems 
#  (see bluemartin.de)
#
##############################################################################
#
# define <name> freeairconnect <seriennummer>
#
##############################################################################

package main;

use strict;
use warnings;
use Time::Local;
use MIME::Base64;
#use Crypt::CBC;
#use Crypt::Rijndael;
use URI::Escape;
use HttpUtils;

my %ControlAutoText = (
	"0" => "Minimum Ventilation",
	"1" => "Humidity Reduction(rel)",
	"2" => "Humidity Reduction(abs)",
	"3" => "Active Cooling",
	"4" => "CO2 Reduction",
	"5" => "Water Insertion",
	"6" => "Outdoor Temp < -22",
	"7" => "Humidity Input",
);

my %StateText = (
	"0" => "Comfort",
	"1" => "Comfort",
	"2" => "Sleep",
	"3" => "Turbo",
	"4" => "Turbocool",
	"5" => "Service",
	"6" => "Test",
	"7" => "Manufacturer",
);
#our $KEYPASSWORD;
 
##############################################################################


sub freeairconnect_Initialize
{
  my ($hash) = @_;
  my $name = $hash->{NAME};

  $hash->{DefFn}        = "freeairconnect_Define";
  $hash->{UndefFn}      = "freeairconnect_Undefine";
  $hash->{DeleteFn}     = "freeairconnect_Delete";
  $hash->{RenameFn}     = "freeairconnect_Rename";
  $hash->{GetFn}        = "freeairconnect_Get";
  $hash->{SetFn}        = "freeairconnect_Set";
  $hash->{AttrFn}       = "freeairconnect_Attr";
  $hash->{AttrList}     = "disable:0,1 interval ".$readingFnAttributes;
  
  return;
}

#######################################################################
sub freeairconnect_Define 
{
  my ($hash, $def) = @_;
  my @args = split m{\s+}xms, $def;

  return "syntax: define <name> freeairconnect <seriennummer>" if(int(@args) != 3 );
  my $name = $hash->{NAME};

  $hash->{helper}{SERIENNUMMER} //= $args[2];
#  $hash->{INTERVAL} //= 60;
  $hash->{ERROR} = 0;

  my $req = eval
  {
    require Crypt::CBC;
    Crypt::CBC->import();
    require Crypt::Rijndael;
    Crypt::Rijndael->import();
    1;
  };

  if($req)
  {
    Log3 $name, 5, "freeairconnect ($name): Define: Setting default attributes";
    $attr{$name}{stateFormat} //= 'OperationMode ComfortLevel<br>ControlAutoText<br>AirFlow m&sup3;/h  HeatRecovery %  EnergySaving W  CO2 ppm';
    $attr{$name}{webCmd} //= 'OperationMode:ComfortLevel';
    $attr{$name}{webCmdLabel} //= 'OperationMode:ComfortLevel';
    $attr{$name}{interval} //= 60;
    Log3 $name, 5, "freeairconnect ($name): Define: setting first timer, update in ".$attr{$name}{interval}." seconds";
    InternalTimer( gettimeofday() + $attr{$name}{interval}, "freeairconnect_GetUpdate", $hash);
  }
  else
  {
    $hash->{STATE} = "Crypt::CBC and Crypt::Rijndael are required!";
    $attr{$name}{disable} = "1";
    return;
  }

  #$hash->{STATE} = "Initialized";

  return;
}

#######################################################################
sub freeairconnect_Undefine 
{
  my ($hash, $arg) = @_;
  my $name = $hash->{NAME};
  RemoveInternalTimer($hash);
  HttpUtils_Close($hash);
  return;
}
#######################################################################
sub freeairconnect_Delete 
{
   my ( $hash, $name ) = @_;
   
   my $index = "freeairconnect_".$name."_passwd";
   setKeyValue($index, undef);
 
   return;
}

#######################################################################
sub freeairconnect_Rename
{
    my ($new, $old) = @_; 
    Log3 $old, 5, "freeairconnect ($old): Rename:  $old $new";
    my $old_index = "freeairconnect_".$old."_passwd";
    my $new_index = "freeairconnect_".$new."_passwd";
   
    my ($err, $old_pwd) = getKeyValue($old_index);
    my $new_pwd = freeairconnect_encryptPassword($new, freeairconnect_decryptPassword($old,$old_pwd));
   
    setKeyValue($new_index, $new_pwd);
    setKeyValue($old_index, undef);
    
    return;

}

#####################################
# checks and stores freeairconnect key used for http call to freeair-connect.de
sub freeairconnect_storePassword
{
    my ($hash, $password) = @_;
    my $name = $hash->{NAME};
    Log3 $name, 5, "freeairconnect ($name): storePassword"; 
    my $index = "freeairconnect_".$hash->{NAME}."_passwd";
    
    my $enc_pwd = freeairconnect_encryptPassword($name, $password);
    
    my $err = setKeyValue($index, $enc_pwd);
    return "error while saving the password - $err" if(defined($err));
    
    return "password successfully saved";
} # end freeairconnect_storePassword

#########################################################################
# encrypts password
sub freeairconnect_encryptPassword
{
    my ($name, $password) = @_;
    Log3 $name, 5, "freeairconnect ($name): encrypts password"; 
    my $index = "freeairconnect_".$name."_passwd";
    my $key = getUniqueId().$index;
    
    my $enc_pwd = "";

## no critic (ProhibitStringyEval)
    if(eval "use Digest::MD5;1")
    {
        $key = Digest::MD5::md5_hex(unpack "H*", $key);
        $key .= Digest::MD5::md5_hex($key);
    }
## use critic (ProhibitStringyEval)    
    for my $char (split //, $password)
    {
        my $encode=chop($key);
        $enc_pwd.=sprintf("%.2x",ord($char)^ord($encode));
        $key=$encode.$key;
    }
    return $enc_pwd;
}

#########################################################################
# decrypts password
sub freeairconnect_decryptPassword
{
   my ($name, $password) = @_;
   Log3 $name, 5, "freeairconnect ($name): decryptPassword"; 
   my $index = "freeairconnect_".$name."_passwd";
   my $key = getUniqueId().$index;
    
   if ( defined($password) ) {
## no critic (ProhibitStringyEval)
      if ( eval "use Digest::MD5;1" ) {
         $key = Digest::MD5::md5_hex(unpack "H*", $key);
         $key .= Digest::MD5::md5_hex($key);
      }
## use critic (ProhibitStringyEval)
      my $dec_pwd = '';
     
      for my $char (map { pack('C', hex($_)) } ($password =~ /(..)/xg)) {
         my $decode=chop($key);
         $dec_pwd.=chr(ord($char)^ord($decode));
         $key=$decode.$key;
      }
     
      return $dec_pwd;
   }
}    
  
  
#####################################
# reads the freeairconnect password
sub freeairconnect_readPassword
{
   my ($hash) = @_;
   my $name = $hash->{NAME};
   Log3 $name, 5, "freeairconnect ($name): storePassword"; 

   my $index = "freeairconnect_".$hash->{NAME}."_passwd";

   my ($password, $err);

   Log3 $name, 5, "freeairconnect ($name): Read freeairconnect password from file";
   ($err, $password) = getKeyValue($index);

   if ( defined($err) ) {
      Log3 $name, 1, "freeairconnect ($name): unable to read freeairconnect password from file: $err";
      return;
   }  
    
   if ( defined($password) ) {
     
      return freeairconnect_decryptPassword($name, $password);
   }
   else {
      Log3 $name, 1, "freeairconnect ($name): No password in file";
      return;
   }
} # end freeairconnect_readPassword

#######################################################################
#SetFn - Set commands
sub freeairconnect_Set 
{
  my ($hash, $name, $command, $parm0) = @_;
  Log3 $name, 5, "freeairconnect ($name): Set command $command"; 
  
  my $usage = "Unknown argument $command, choose one of key interval ComfortLevel:1,2,3,4,5 OperationMode:Comfort,Sleep,Turbo,Turbocool";
  return $usage unless ($command =~ "key|interval|ComfortLevel|OperationMode");
  my ($postdata, $OM, $CL, $header, $nextupdate);
  if ( lc $command eq 'key') {
      if ($parm0) 
      {
#         $KEYPASSWORD = $parm0;
         return freeairconnect_storePassword ( $hash, $parm0 );
      } else {
        return "Usage: set $name key <yourkey>";
      }
  
  } 
  if ( lc $command eq 'interval') {
      if ($parm0 < 60) {
        return "Inverval must be greater or equal 60 (consider the load on freeair-connect servers)";
      } else {
        Log3 $name, 5, "freeairconnect ($name): Set $command $parm0";
        $hash->{INTERVAL} = $parm0;
        Log3 $name, 5, "freeairconnect ($name): Set $command $parm0 - removing old timer";
        RemoveInternalTimer($hash);
        $nextupdate = gettimeofday()+$hash->{INTERVAL};
        $hash->{helper}{NextUpdate} = $nextupdate;
        $hash->{helper}{NextUpdateFormatted} = FmtDateTime($nextupdate);
        Log3 $name, 5, "freeairconnect ($name): Set $command $parm0 - setting new timer to $nextupdate";
        InternalTimer($nextupdate, "freeairconnect_GetUpdate", $hash);


      }
  } 
  if ( lc $command eq 'comfortlevel') {
      if ($parm0 !~ "[1-5]") {
        return "ComfortLevel must be 1 2 3 4 or 5";
      } else {
        Log3 $name, 5, "freeairconnect ($name): Set $command $parm0";
        $hash->{helper}{UpdatingComfortLevel} = 1;
        freeairconnect_GetUpdate($hash); #must reread because we must send both OM and CL
        $CL = $parm0;
        $postdata = "serObject=CL%3D".$CL
          ."%26OM%3D".$hash->{READINGS}{OperationModeNum}
          ."%26serialnumber%3D".$hash->{helper}{SERIENNUMMER}
          ."%26device%3D1";
        $header = "Referer: https://www.freeair-connect.de/tabs.php?seriennumber=".$hash->{helper}{SERIENNUMMER};
        Log3 $name, 5, "freeairconnect ($name): Set $command $parm0 - sending postdata";
        
        HttpUtils_NonblockingGet({
          url => 'https://www.freeair-connect.de/buttonUserAjax.php',
          noshutdown => 1,
          hash => $hash,
          method => 'POST',
          data => $postdata,
          header => $header,
          keepalive => 1,
          callback => sub { my ($httphash, $httperr, $httpdata) = @_;
                                Log3 $name, 4,"freeairconnect ($name): ERR:$httperr DATA:\n".$httpdata;
                                $httpdata =~ s/\r|\n//gx;
                                if ($httperr || $httpdata ne "1") {
                                  Log3 $name, 2, "freeairconnect ($name): Error POST setting ComfortLevel ERR: $httperr DATA: $httpdata";
                                } else {
                                  Log3 $name, 5, "freeairconnect ($name): Posted comfortlevel $CL successfully";
                                }
                              } ,
        });

        readingsSingleUpdate($hash, "ComfortLevel", $CL, 1);

        RemoveInternalTimer($hash);
        $nextupdate = gettimeofday()+90; #Reread data in 90 seconds
        Log3 $name, 5, "freeairconnect ($name): Set $command $parm0 - setting new timer $nextupdate";
        $hash->{helper}{NextUpdate} = $nextupdate;
        $hash->{helper}{NextUpdateFormatted} = FmtDateTime($nextupdate);
        InternalTimer($nextupdate, "freeairconnect_GetUpdate", $hash);

      }
  } 
  if ( lc $command eq 'operationmode') {
      if ((lc $parm0) !~ "(comfort|sleep|turbo|turbocool)") {
        return "Unknown OperationMode ".$parm0.", choose one of Comfort, Sleep, Turbo, Turbocool";
      } else {
        Log3 $name, 5, "freeairconnect ($name): Set $command $parm0";
        $hash->{helper}{UpdatingOperationMode} = 1;
        freeairconnect_GetUpdate($hash); #must reread because we must send both OM and CL
        $OM = 1; #Comfort by default if no value provided
        $OM = 2 if ($parm0 eq "Sleep");
        $OM = 3 if ($parm0 eq "Turbo");
        $OM = 4 if ($parm0 eq "Turbocool");
        $CL = $hash->{READINGS}{ComfortLevel}; 
        $CL = 3 if ($CL > 5 or $CL <= 0); #if we were previously in sleep mode, the comfort level has been set to 8, which is not valid
        $postdata = "serObject=CL%3D".$CL
          ."%26OM%3D".$OM
          ."%26serialnumber%3D".$hash->{helper}{SERIENNUMMER}
          ."%26device%3D1";
        $header = "Referer: https://www.freeair-connect.de/tabs.php?seriennumber=".$hash->{helper}{SERIENNUMMER};
        Log3 $name, 5, "freeairconnect ($name): Set $command $parm0 - sending postdata";
        
        HttpUtils_NonblockingGet({
          url => 'https://www.freeair-connect.de/buttonUserAjax.php',
          noshutdown => 1,
          hash => $hash,
          method => 'POST',
          data => $postdata,
          header => $header,
          keepalive => 1,
          callback => sub { my ($httphash, $httperr, $httpdata) = @_;
                                Log3 $name, 4,"freeairconnect ($name): ERR:$httperr DATA:".length($httpdata);
                                $httpdata =~ s/\r|\n//gx;
                                if ($httperr || $httpdata ne "1") {
                                  Log3 $name, 2, "freeairconnect ($name): Error POST setting operationmode ERR: $httperr DATA: $httpdata";
                                } else {
                                  Log3 $name, 5, "freeairconnect ($name): Posted operationmode $OM successfully";
                                }
                              } ,
        });

        readingsSingleUpdate($hash, "OperationModeNum", $OM, 1);
        readingsSingleUpdate($hash, "OperationMode", $StateText{$OM}, 1);

        RemoveInternalTimer($hash);
        $nextupdate = gettimeofday()+90; #Reread data in 90 seconds
        Log3 $name, 5, "freeairconnect ($name): Set $command $parm0 - setting new timer $nextupdate";
        $hash->{helper}{NextUpdate} = $nextupdate;
        $hash->{helper}{NextUpdateFormatted} = FmtDateTime($nextupdate);
        InternalTimer($nextupdate, "freeairconnect_GetUpdate", $hash, 1);

      }
  } 
  return;    
}

#######################################################################
sub freeairconnect_Get 
{
  my ($hash, @a) = @_;
  my $command = $a[1];
  my $parameter;
  $parameter = $a[2] if(defined($a[2]));
  my $name = $hash->{NAME};
  Log3 $name, 5, "freeairconnect ($name): Get";

  my $usage = "Unknown argument $command, choose one of data:noArg storedKey:noArg";

  return $usage if ($command !~ /data|storedKey/x);
  if ($command eq "data") {
    RemoveInternalTimer($hash);
  
    if(AttrVal($name, "disable", 0) eq "1") {
      $hash->{STATE} = "disabled";
      return "freeairconnect $name is disabled. Aborting...";
    }
  
    freeairconnect_GetUpdate($hash);
    return;
  }
  if ($command eq "storedKey") {
    return "storedKey = ".freeairconnect_readPassword($hash);
  }
  return;
}


#######################################################################
sub freeairconnect_GetUpdate 
{
  my ($hash) = @_;
  my $name = $hash->{NAME};
  Log3 $name, 5, "freeairconnect ($name): GetUpdate";
  if(AttrVal($name, "disable", 0) eq "1") {
    $hash->{STATE} = "disabled";
    Log3 ($name, 2, "freeairconnect ($name) is disabled, data update cancelled.");
    return;
  }

  my $url="https://www.freeair-connect.de/getDataHexAjax.php";
  Log3 ($name, 5, "freeairconnect ($name): Getting URL $url");
  my $postdata = "serObject=serialnumber%3D".$hash->{helper}{SERIENNUMMER};
  Log3 $name, 5, "freeairconnect ($name): GetUpdate: sending postdata";

  HttpUtils_NonblockingGet({
      url => $url,
      noshutdown => 1,
      hash => $hash,
      method => 'POST',
	    data => $postdata,
      keepalive => 1,
      callback => \&freeairconnect_Parse,
    });
#  $hash->{INTERVAL} //= 60;
  my $interval = 60;
  $interval = $attr{$name}{interval}  if ($attr{$name}{interval} >= 60);
  $interval = $hash->{INTERVAL} if ($hash->{INTERVAL} && $hash->{INTERVAL} >= 60);
  Log3 $name, 5, "freeairconnect ($name): GetUpdate: setting new interval $interval";
  my $nextupdate = gettimeofday()+$interval;
  Log3 $name, 5, "freeairconnect ($name): GetUpdate - setting new timer $nextupdate";
  $hash->{helper}{NextUpdate} = $nextupdate;
  $hash->{helper}{NextUpdateFormatted} = FmtDateTime($nextupdate);
  RemoveInternalTimer($hash);
  InternalTimer($nextupdate, "freeairconnect_GetUpdate", $hash);
  Log3 $name, 5, "freeairconnect ($name): GetUpdate: new interval set";

  return;
}


#######################################################################
sub freeairconnect_Parse
{
  my ($param, $err, $data) = @_;

  my $hash = $param->{hash};
  my $name = $hash->{NAME};
  Log3 $name, 5, "freeairconnect ($name): Params Parse = $param, $err, ".substr($data,0,255);
  if( $err )
  {
    Log3 $name, 1, "freeairconnect ($name): URL error (".($hash->{ERROR}+1)."): ".$err;
    my $nextupdate = gettimeofday()+( (60*$hash->{ERROR}) + 60 );
    $hash->{helper}{NextUpdate} = $nextupdate;
    $hash->{helper}{NextUpdateFormatted} = FmtDateTime($nextupdate);
    RemoveInternalTimer($hash);
    InternalTimer($nextupdate, "freeairconnect_GetUpdate", $hash);
    $hash->{STATE} = "error" if($hash->{ERROR} > 1);
    $hash->{ERROR} = $hash->{ERROR}+1;
    return;
  }
  Log3 $name, 5, "freeairconnect ($name): Parse: Starting";

  $hash->{ERROR} = 0;
  
  my ($rawdata, $datatime) = $data =~ /(.{50,70})timestamp(.{19})/x;
  Log3 $name, 5, "freeairconnect ($name): Handling data $rawdata";
  if (!$rawdata) {
    Log3 $name, 2, "freeairconnect ($name): Warning: could not extract first chunk of data from raw data. Aborting update.";
    return;
  }

#
# Extract and update readings
#
  readingsBeginUpdate($hash); 
  readingsBulkUpdate($hash, "lastDataTimestamp", $datatime);
  readingsBulkUpdate($hash, "lastRawData", $rawdata);
     
   $rawdata = uri_unescape($rawdata);
  if (length($rawdata) != 64) {
    Log3 $name, 2, "freeairconnect ($name): Received buffer with wrong length ".length($rawdata)." instead of expected 64";
	return;
  }
   $rawdata = decode_base64($rawdata);

   my $iv = pack "H*", "000102030405060708090a0b0c0d0e0f";
#   my $key = $attr{$name}{key};
   my $KEYPASSWORD = freeairconnect_readPassword($hash);
   if (!defined $KEYPASSWORD) {
     Log3 $name, 2, "freeairconnect ($name): Key not defined. Parsing not possible. Returning";
     return;
   }

   if (length($KEYPASSWORD) < 16) {
     $KEYPASSWORD .= '0'x(16 - length $KEYPASSWORD);
   }
   my $cipher = Crypt::CBC->new(
      -key => $KEYPASSWORD,
      -literal_key => 1,
      -iv => $iv,
      -keysize => 16,
      -cipher => 'Rijndael',
      -header => 'none');

   my $plaintext  = $cipher->decrypt($rawdata);
   my @result = unpack("C*", $plaintext);
   my @bitResult = unpack("B*", $plaintext);
   my $bitString = join("",@bitResult);
   Log3 $name, 5, "freeairconnect ($name): stringToBytes = $bitString";
   $hash->{helper}{bytes} = sprintf("@result");
   Log3 $name, 5, "freeairconnect ($name): stringToBytes = @result";

# Probabilitycheck 
   my $DIP = freeairconnect_extractValueFromBits("DIPSwitch", $bitString);
   my $ErrorState = freeairconnect_extractValueFromBits("ErrorState", $bitString);
#   if ($ErrorState ne "0" and $DIP ne ReadingsVal($name, "DIPSwitch", 0)) {
#     readingsEndUpdate($hash, 1);
#     Log3 $name, 3, "freeairconnect ($name): Ignoring probably wrong data $rawdata";
#     $hash->{UPDATED} = FmtDateTime(time());
#     return;
#   }
     
# direct readings
   readingsBulkUpdate($hash, "S1", $result[41] );
   readingsBulkUpdate($hash, "S2", $result[42] );
   readingsBulkUpdate($hash, "S3", $result[43] );
   readingsBulkUpdate($hash, "S4", $result[44] );
   readingsBulkUpdate($hash, "S5", $result[45] );
   readingsBulkUpdate($hash, "S6", $result[46] );
   

# simple readings from bits
  foreach my $simpleReading ("HumRedMode", "FanLim2ndRoom", "b2ndRoomOnly20", "SumCooling",
    "ErrorFileNr", "ErrorLineNr", "FilterSupplyFul", 
    "FilterExtractFul", "VentPosExtract", "VentPosBath", "VentPosSupply", 
    "VentPosBypass", "CtrlSetSupVent", "CtrlSetExtVent", "CtrlSet2ndVent", 
    "CtrlSetBypVent", "ErrorCode", "FilterHours", "OperatingHours", 
    "Deicing", "FSC", "FEC", "CSU", "CFA", "DIPSwitch") {
      readingsBulkUpdate($hash, $simpleReading, freeairconnect_extractValueFromBits($simpleReading, $bitString));
  }

# calculated readings or readings needed in calculation
   my $HumOutdoor = $result[0];
   readingsBulkUpdate($hash, "HumOutdoor", $HumOutdoor);
   my $HumExtract = $result[1];
   readingsBulkUpdate($hash, "HumExtract", $HumExtract);

   my $TempOutdoor = freeairconnect_toSigned( freeairconnect_extractValueFromBits("TempOutdoor", $bitString), 11) / 8;
   readingsBulkUpdate($hash, "TempOutdoor", $TempOutdoor);

   my $TempExtract = freeairconnect_toSigned( freeairconnect_extractValueFromBits("TempExtract", $bitString), 11) / 8;
   readingsBulkUpdate($hash, "TempExtract", $TempExtract);

   my $TempSupply = freeairconnect_toSigned( freeairconnect_extractValueFromBits("TempSupply", $bitString), 11) / 8;
   readingsBulkUpdate($hash, "TempSupply", $TempSupply);

   my $TempExhaust = freeairconnect_toSigned( freeairconnect_extractValueFromBits("TempExhaust", $bitString), 11) / 8;
   readingsBulkUpdate($hash, "TempExhaust", $TempExhaust);

   my $TempVirtSupExit = freeairconnect_toSigned( freeairconnect_extractValueFromBits("TempVirtSupExit", $bitString), 11) / 8;
   readingsBulkUpdate($hash, "TempVirtSupExit", $TempVirtSupExit);

   readingsBulkUpdate($hash, "AbsHumOutdoor", freeairconnect_absHum($TempOutdoor, $HumOutdoor));
   readingsBulkUpdate($hash, "AbsHumExtract", freeairconnect_absHum($TempExtract, $HumExtract));

   my $CO2 = freeairconnect_extractValueFromBits("CO2", $bitString) * 16;
   readingsBulkUpdate($hash, "CO2", $CO2);

   my $Pressure = freeairconnect_extractValueFromBits("Pressure", $bitString) +700;
   readingsBulkUpdate($hash, "Pressure", $Pressure);

   if (!defined $hash->{helper}{UpdatingComfortLevel}) {
      my $ComfortLevel = freeairconnect_extractValueFromBits("ComfortLevel", $bitString) + 1;
      readingsBulkUpdate($hash, "ComfortLevel", $ComfortLevel);
   } else {
      $hash->{helper}{UpdatingComfortLevel} = undef;
   }

   if (!defined $hash->{helper}{UpdatingOperationMode}) {
      my $OperationModeNum = freeairconnect_extractValueFromBits("OperationModeNum", $bitString);
      readingsBulkUpdate($hash, "OperationModeNum", $OperationModeNum);
      readingsBulkUpdate($hash, "OperationMode", $StateText{$OperationModeNum});
   } else {
      $hash->{helper}{UpdatingOperationMode} = undef;
   }

   my $FanSpeed = freeairconnect_extractValueFromBits("FanSpeed", $bitString);
   readingsBulkUpdate($hash, "FanSpeed", $FanSpeed );

   my $FanSupplyRPM = freeairconnect_extractValueFromBits("FanSupplyRPM", $bitString);
   readingsBulkUpdate($hash, "FanSupplyRPM", $FanSupplyRPM );

   my $FanExtractRPM =  freeairconnect_extractValueFromBits("FanExtractRPM", $bitString);
   readingsBulkUpdate($hash, "FanExtractRPM", $FanExtractRPM );
   
   my $TrafficLightFilterSupply = freeairconnect_filterSupplyStatus($FanSupplyRPM, $FanSpeed);
   readingsBulkUpdate($hash, "TrafficLightFilterSupply", $TrafficLightFilterSupply );

   my $TrafficLightFilterExtract = freeairconnect_filterExtractStatus($FanExtractRPM, $FanSpeed);
   readingsBulkUpdate($hash, "TrafficLightFilterExtract", $TrafficLightFilterExtract );

   my $AirFlowAve = freeairconnect_extractValueFromBits("AirFlowAve", $bitString);
   my $AirFlow;
   if ($FanSpeed > 2) {
      $AirFlow = $FanSpeed*10;
   } else {
      $AirFlow = $AirFlowAve;
   }
   readingsBulkUpdate($hash, "AirFlowAve", $AirFlowAve );
   readingsBulkUpdate($hash, "AirFlow", $AirFlow );

   my $ControlAuto = freeairconnect_extractValueFromBits("ControlAuto", $bitString);
   readingsBulkUpdate($hash, "ControlAuto", $ControlAuto );
   readingsBulkUpdate($hash, "ControlAutoText", $ControlAutoText{$ControlAuto} );
  
   my $RSSI = freeairconnect_toSigned( freeairconnect_extractValueFromBits("RSSI", $bitString), 8);
   readingsBulkUpdate($hash, "RSSI", $RSSI );
   
   my $HeatRecovery;
   if ($AirFlow == 0 or abs($TempExtract - $TempOutdoor) < 2) {
      $HeatRecovery = 100;
   } else {
      $HeatRecovery = sprintf ("%.1f", 
         100 * (1 - ($TempExtract - $TempSupply ) /($TempExtract - $TempOutdoor))+0.5);   
   }
   readingsBulkUpdate($hash, "HeatRecovery", $HeatRecovery );

   my $EnergySaving;
   if (abs($TempExtract - $TempOutdoor) < 2) {
      $EnergySaving = 0;
   } else {
      $EnergySaving = sprintf ("%.1f", 
         $AirFlow * ($TempSupply - $TempOutdoor) / 3 + 0.5 );   
   }
   readingsBulkUpdate($hash, "EnergySaving", $EnergySaving );

   my $TrafficLightHumidity;
   if ($HumExtract < 10 or $HumExtract > 85) {
      $TrafficLightHumidity = 4;
   } elsif ($HumExtract < 20 or $HumExtract > 70) {
      $TrafficLightHumidity = 3;
   } elsif ($HumExtract < 20 or $HumExtract > 70) {
      $TrafficLightHumidity = 2;
   } else {
      $TrafficLightHumidity = 1;
   }
   readingsBulkUpdate($hash, "TrafficLightHumidity", $TrafficLightHumidity );

   my $TrafficLightCO2;
   if ($CO2 < 1000) {
      $TrafficLightCO2 = 1;
   } elsif ($CO2 < 1700) {
      $TrafficLightCO2 = 2;
   } elsif ($CO2 < 2500) {
      $TrafficLightCO2 = 3;
   } else {
      $TrafficLightCO2 = 4;
   }
   readingsBulkUpdate($hash, "TrafficLightCO2", $TrafficLightCO2 );

   readingsBulkUpdate($hash, "ErrorState", $ErrorState );
   
#Bugsuche
#   if ($ErrorState ne "0")
#   {   Log3 $name, 1, "freeairconnect ($name): Params Parse = $param, Err = $err, Data = $data, KEYPASSWORD = $KEYPASSWORD";
#       Log3 $name, 1, "freeairconnect ($name): stringToBytes = $bitString";
#
#   }

  readingsEndUpdate($hash, 1);
  
  freeairconnect_getErrorText($hash, $ErrorState, $hash->{helper}{SERIENNUMMER});

  $hash->{UPDATED} = FmtDateTime(time());
  return;
}

#######################################################################
sub freeairconnect_Attr
{
  my ($cmd, $name, $attrName, $attrVal) = @_;

  my $hash = $defs{$name};

  if( $attrName eq "disable" ) {
    RemoveInternalTimer($hash);
    if( $cmd eq "set" && $attrVal ne "0" ) {
      $attrVal = 1;
    } else {
      $attr{$name}{$attrName} = 0;
      freeairconnect_GetUpdate($hash);
    }
  }

  my $nextupdate;  
  if ($attrName eq "interval") {
      if ($attrVal < 60) {
        return "Inverval must be greater or equal 60 (consider the load on freeair-connect servers)";
      } else {
        $attr{$name}{interval} = $attrVal;
        Log3 $name, 5, "freeairconnect ($name): Attr: interval set to $attrName";
        if ($init_done) {
          RemoveInternalTimer($hash);
          $nextupdate = gettimeofday()+$attrVal;
          $hash->{helper}{NextUpdate} = $nextupdate;
          $hash->{helper}{NextUpdateFormatted} = FmtDateTime($nextupdate);
          InternalTimer($nextupdate, "freeairconnect_GetUpdate", $hash);
          Log3 $name, 5, "freeairconnect ($name): Attr: new timer set to $nextupdate";
        }

      }
  }    
    
  return;
}
#######################################################################
sub freeairconnect_toSigned
{
   my ($num, $potenz) = @_;
   my $maxUn=2**$potenz;
   if($num >= ($maxUn / 2)){$num = $num - $maxUn}
   return $num;
}

#######################################################################
sub freeairconnect_extractValueFromBits 
{
    my ($reading, $bits) = @_;

# Parameters as they are in the createPrimBlobObject javascript function of the site
# When the javascript function uses lowPlusHigh(low,high,superHigh), the three parameters of each low, high and superhigh 
#   are written one after another in reverse order (most significant first)
# In concatenations, the function always uses the 7 least significant bits of a byte only, thus [..., 0, 7] when whole byte
# 
# Example: var division31=[4,3];var dividedByte31=divideByte(division31,parsedBlob[31]);
#          var uTempExhaustHigh=dividedByte31[0];
#          var uTempExhaustLow=parsedBlob[4];
#          var iTempExhaust=lowPlusHigh(uTempExhaustLow,uTempExhaustHigh);
#
#                                          ------------------- high = byte number 31 (parsedBlob[31])
#                                         |                        (no superHigh here, otherwise it would come first)
#                                         |   ---------------- from pos 0 (lsb) (first part of division - dividedByte31[0]).
#                                         |  |                     (if it were 2nd part dividedByte31[1], then start position would be 4)
#                                         |  |   ------------- with length 4 (the first part has length 4 - division31=[4,...])
#                                         |  |  |    --------- low = byte number 4 (parsedBlob[4])
#                                         |  |  |   |   ------ from pos 0 (lsb)
#                                         |  |  |   |  |   --- with length 7 (eigth bit msb not used in concatenations)
#                                         |  |  |   |  |  |
#                                         V  V  V   V  V  V
    my %split = ( TempExhaust        => [31, 0, 4,  4, 0, 7],
                  TempSupply         => [29, 0, 4,  2, 0, 7],
                  TempOutdoor        => [32, 0, 4,  3, 0, 7],
                  TempExtract        => [30, 0, 4,  5, 0, 7],
                  TempVirtSupExit    => [33, 0, 4,  6, 0, 7],
                  CO2                => [36, 5, 1, 13, 0, 7],
                  Pressure           => [39, 0, 5, 34, 0, 4],
                  ComfortLevel       => [29, 4, 3],
                  OperationModeNum   => [30, 4, 3],
                  HumRedMode         => [37, 5, 1],
                  FanLim2ndRoom      => [35, 6, 1],
                  b2ndRoomOnly20     => [35, 5, 1],
                  SumCooling         => [37, 6, 1],
                  ErrorState         => [24, 0, 5],
                  FanSpeed           => [38, 0, 4],
                  FanSupplyRPM       => [37, 0, 5,  9, 0, 7],
                  FanExtractRPM      => [36, 0, 5,  7, 0, 7],
                  AirFlowAve         => [35, 0, 5],
                  FilterSupplyFul    => [34, 5, 1],
                  FilterExtractFul   => [34, 6, 1],
                  VentPosExtract     => [26, 0, 5],
                  VentPosBath        => [27, 0, 5],
                  VentPosSupply      => [25, 0, 5],
                  VentPosBypass      => [28, 0, 5],
                  ControlAuto        => [31, 4, 3],
                  CtrlSetSupVent     => [25, 5, 2],
                  CtrlSetExtVent     => [26, 5, 2],
                  CtrlSet2ndVent     => [27, 5, 2],
                  CtrlSetBypVent     => [28, 5, 2],
                  ErrorCode          => [40, 6, 1, 12, 0, 7],
                  FilterHours        => [40, 4, 2, 17, 0, 7, 16, 0, 7],
                  OperatingHours     => [40, 0, 4, 15, 0, 7, 14, 0, 7],
                  Deicing            => [23, 6, 1],
                  FSC                => [38, 4, 1, 18, 0, 7],
                  FEC                => [38, 5, 1, 19, 0, 7],
                  CSU                => [38, 6, 1, 20, 0, 7],
                  CFA                => [34, 4, 1, 21, 0, 7],
                  RSSI               => [47, 0, 8],
                  DefrostExhaust     => [24, 5, 2],
                  DIPSwitch          => [36, 6, 1,  8, 0, 7],
                  ErrorLineNr        => [39, 5, 2, 10, 0, 7, 11, 0, 7],
                  ErrorFileNr        => [23, 0, 6],
            );

    my $result;
    my @splitparams = @{$split{$reading}};
    my $i = 0;
    while ($i < int(@splitparams) ) {
      my $byte = $splitparams[$i++];
      my $start = $splitparams[$i++];
      my $length = $splitparams[$i++];
      $result .= substr($bits, 8*$byte + 8 - $start - $length,
          $length);
    }
    $result = oct("0b".$result);
    return $result;
}

sub freeairconnect_filterStatus
{
  my ($fanRPM, $fanSpeed, @filterRPMs) = @_;
  for (my $i = 0; $filterRPMs[$i];$i++)  {
    next if ($filterRPMs[$i][0] < $fanSpeed);
    my $nDiff  = $filterRPMs[$i][2] - $filterRPMs[$i][1];
    return 100 if ($fanRPM < ($filterRPMs[$i][1] - $nDiff/2));
    return 1 if ($fanRPM < ($filterRPMs[$i][1] + $nDiff*0.4));
    return 2 if ($fanRPM < ($filterRPMs[$i][1] + $nDiff*0.7));
    return 3 if ($fanRPM < ($filterRPMs[$i][1] + $nDiff*0.95));
    return 4;
  }
  return 1;
}

sub freeairconnect_filterExtractStatus
{
  my ($fanExtractRPM,$fanSpeed) = @_;
  my @fanExtractRPMs = (
    [20,920,1560],
    [30,1040,1680],
    [40,1260,1900],
    [50,1480,2200],
    [60,1700,2420],
    [70,1910,2710],
    [85,2210,2930],
    [100,2480,3200],
    [0,0,0],
  );
  return freeairconnect_filterStatus($fanExtractRPM,$fanSpeed,@fanExtractRPMs);
}

sub freeairconnect_filterSupplyStatus
{
  my ($fanSupplyRPM,$fanSpeed) = @_;
  my @fanSupplyRPMs = (
    [20,870,1510],
    [30,1000,1640],
    [40,1230,1870],
    [50,1460,2100],
    [60,1690,2410],
    [70,1910,2630],
    [85,2230,2950],
    [100,2540,3260],
    [0,0,0],
  );
  return freeairconnect_filterStatus($fanSupplyRPM,$fanSpeed,@fanSupplyRPMs);
  
}

sub freeairconnect_absHum
{
  my ($temp, $hum) = @_;
  
  my @ahPlusG10m3 = (49, 52, 56, 60, 64, 69, 73, 78, 84, 89, 95, 102, 108, 115, 123, 131, 139, 148, 157, 167, 177, 188, 199, 212, 224, 238, 252, 267, 283, 299, 317, 335, 354, 375, 396, 419, 442, 467, 494, 521, 550, 581, 613, 647, 683, 721, 760, 802, 846, 893, 942);
  my @ahMinusG10m3 = (49, 45, 42, 39, 37, 34, 32, 29, 27, 25, 23, 21, 20, 18, 17, 15, 14, 13, 12, 11, 10);

  my $absHum;
  if ($temp > 0) {
     if ($temp > 50) {
        $absHum = 1000 / 10 * $hum / 100;
     }
     else {
        $absHum = $ahPlusG10m3[sprintf("%.0f",$temp)] / 10 * $hum / 100;
     }
  } else {
     if (abs($temp) > 20) {
        $absHum = 5 / 10 * $hum / 100;
     } else {
        $absHum = $ahMinusG10m3[abs(sprintf("%.0f",$temp))] / 10 * $hum / 100;
     }
  }

  return sprintf ("%.1f", $absHum);
}
###############################################################################
# get errortext from errorstate
sub freeairconnect_getErrorText
{
  my ($hash, $errorState, $serial) = @_;
  if ($errorState == 22 or $errorState == 0) {
    #no error
    readingsSingleUpdate($hash, "ErrorText", "", 1);
    return;
  }
  
  my $errorBin = substr(unpack("B32", pack("N", $errorState)), -5);
  my $postdata = "serObject=err%3D".$errorBin."%26serialnumber%3D".$serial."%26device%3D1";
  my $header = "Referer: https://www.freeair-connect.de/tabs.php?seriennumber=".$serial;
  HttpUtils_NonblockingGet({
          url => 'https://www.freeair-connect.de/getErrorTextLong.php',
          noshutdown => 1,
          hash => $hash,
          method => 'POST',
          data => $postdata,
          header => $header,
          callback => \&freeairconnect_ParseError ,
        });
  return;
}

sub freeairconnect_ParseError
{
  my ($param, $err, $data) = @_;
  my $hash = $param->{hash};
  my $name = $hash->{NAME};
  my $message;
  if( $err )
  {
    Log3 $name, 1, "freeairconnect ($name): URL error (".($hash->{ERROR}+1)."): ".$err;
  } else {
    ($message) = $data =~ m/en=(.*?)&/xms;
    $message = uri_unescape($message);
    $message =~ s/\+/\ /gx;
    Log3 $name, 5, "freeairconnect ($name) : $data - Errortext = $message";
    readingsSingleUpdate($hash, "ErrorText", $message, 1);
  }
  return;
}
  

1;

=pod
=item device
=item summary Control airflow systems freeair-connect
=begin html

<a name="freeairconnect"></a>
<h3>freeairconnect</h3>
<ul>
  This module reads and controls bluMartin freeair-connect airflow systems <br/>
  It requires the Perl modules Crypt::CBC and Crypt::Rijndael to be installed. On debian, sudo apt install libcrypt-cbc-perl and libcrypt-rijndael-perl
  <br/><br/>
  <b>Define</b>
  <ul>
    <code>define &lt;name&gt; freeairconnect &lt;Serialnumber&gt;</code>
    <br>
    Example: <code>define freeair100 freeairconnect 123456</code>
    <br>
    <li><code>Serialnumber</code>
      <br>
      Only the serialnumber used to access the website freeair-connect.de (without the label/name after it)
    </li><br>
    Immediately after the definition, you should set your key with
    <br>
    <code>set freeair100 key v3rY5secret!#</code>
    <br>&nbsp;
  </ul>
  <br>
  <b>Get</b>
   <ul>
      <li><code>data</code>
      <br>
      Manually trigger data update
      </li><br>
      <li><code>storedKey</code>
      <br>
      Get stored cipher key from passwords file
      </li><br>
  </ul>
  <b>Set</b>
   <ul>
      <li><code>key</code>
      <br>
      Key/password used to decrypt the data as in the webinterface. This is the first thing to do after the definition of the device.
      It will be offuscated and stored in the password file of Fhem
      </li><br>
      <li><code>interval</code>
      <br>
      Set the refresh interval in seconds for the data (default 60). Minimum 60 not to overload the freeair-connect servers. 
      This parameter overrides the corresponding attribute but is not persistent after restart of fhem.
      </li><br>
      <li><code>OperationMode</code>
      <br>
      Set the operation mode of the device (Comfort, Sleep, Turbo...)
      </li><br>
      <li><code>ComfortLevel</code>
      <br>
      Set the comfort level of the device (0 to 5)
      </li><br>
  </ul>
  <br>
  <b>Readings</b>
   <ul>
      <li><code>lastRawData</code>
      <br>
      Last raw main chunk data before decoding the readings
      </li><br>
      <li><code>lastDataTimeStamp</code>
      <br>
      Last value of actualisation timestamp of the data on freeair-connect site. This is <i>not</i> the last read done by Fhem.
      </li><br>
      <li><code><i>TrafficLight.* Readings</i></code>
      <br>
      1 = green, 2 = yellow, 3 = orange, 4 = red
      </li><br>
      <li><code><i>Other Readings</i></code>
      <br>
      As on the website, main page and details.
      </li><br>
  </ul>
  <br>
   <b>Attributes</b>
   <ul>
      <li><code>disable</code>
         <br>
         If set to 1, the polling of the website is disabled
      </li><br>
      <li><code>interval</code>
         <br>
         The refresh interval in seconds for the data (default 60). Minimum 60 not to overload the freeair-connect servers.
         This attribute can be overridden by the corresponding set command. In that case, the real interval can be found in the internal INTERVAL.
      </li><br>
  </ul>
</ul>

=end html

=cut
