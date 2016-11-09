<?
class EnergyreportqatestController extends Delta_Controller_Action
  {
	  public function indexAction()
	    {
            set_time_limit(1500);    // added after build 2.1.124 to make the script still working as expected.
		    $this->_helper->viewRenderer->setNoRender();
        	    $this->_helper->layout->disableLayout();
	/*			
	  $reportDesign = 'Consumption';
	  $reportName = 'Consumption report 001';
	  Report::deleteByName($reportName);
	  $reportId = Report::createReport($reportName, $reportDesign);
	  $queueId = NULL;
	  
	  Report_Param::createParam($reportId, $queueId, 'Report Title', 'Testing Report Title');
      Report_Param::createParam($reportId, $queueId, 'ReportType', 'Electric_Energy');
      Report_Param::createParam($reportId, $queueId, 'Site', '');
      Report_Param::createParam($reportId, $queueId, 'Year', '2016');
	  Report_Param::createParam($reportId, $queueId, 'Baseline Year', '2015');
	  Report_Param::createParam($reportId, $queueId, 'BaselineVisible', '0');
	  Report_Param::createParam($reportId, $queueId, '_Locale', Delta_Language::GetLocale());
	  
	  $meterNode = Report_Meter::createMeterNode();
	  Report_Param::createParam($reportId, $queueId, 'Meters', $meterNode);
	  
	  $Parent=$meterNode;
	  $Area=NULL;
	  $Meter='73fb5839-1c63-11e6-9987-000af787c4bb';
	  $Name='Cube DB Power Meter';
	  $Order=0;
	  Report_Meter::createMeterNode($Parent, $Area, $Meter, $Name, $Order);
	  
	  echo('<br>'.$reportDesign.' report: '.$reportName.' is crerated (id: '.$reportId.')');
	*/	    
      // create 1 report for each design that exists
      //$reportId = array();
      //$reportName = array();
      //$Created = 0;
      //foreach (Report::getDesigns() as $design)
      //              {
	  //				  echo('report design:'.$design);
      //                for($i = 1; $i <= 5; $i++)
      //                {
	  //					 $reportName[$design] = $design.'_Test'.$i; 
	  //					 Report::deleteByName($reportName[$design]);
      //                   $reportId[$design] = Report::createReport($reportName[$design], $design);
      //                   $Created++;
      //                  
      //                }
      //                
      //              }
      //           
	  //     
      //      echo('Reports created:'.Delta_Db::$Report->count()); 
      }
	  
	  public function createreportAction()
	    {
            set_time_limit(1500);    // added after build 2.1.124 to make the script still working as expected.
		    $this->_helper->viewRenderer->setNoRender();
        	    $this->_helper->layout->disableLayout();
				
	  $reportDesign = 'Consumption';
	  $reportName = 'Consumption report 001';
	  Report::deleteByName($reportName);
	  $reportId = Report::createReport($reportName, $reportDesign);
	  $queueId = NULL;
	  
	  Report_Param::createParam($reportId, $queueId, 'Report Title', 'Testing Report Title');
      Report_Param::createParam($reportId, $queueId, 'ReportType', 'Electric_Energy');
      Report_Param::createParam($reportId, $queueId, 'Site', '');
      Report_Param::createParam($reportId, $queueId, 'Year', '2016');
	  Report_Param::createParam($reportId, $queueId, 'Baseline Year', '2015');
	  Report_Param::createParam($reportId, $queueId, 'BaselineVisible', '0');
	  Report_Param::createParam($reportId, $queueId, '_Locale', Delta_Language::GetLocale());
	  
	  $meterNode = Report_Meter::createMeterNode();
	  Report_Param::createParam($reportId, $queueId, 'Meters', $meterNode);
	  
	  $Parent=$meterNode;
	  $Area=NULL;
	  $Meter='73fb5839-1c63-11e6-9987-000af787c4bb';
	  $Name='Cube DB Power Meter';
	  $Order=0;
	  Report_Meter::createMeterNode($Parent, $Area, $Meter, $Name, $Order);
	  
	  echo('<br>'.$reportDesign.' report: '.$reportName.' is crerated (id: '.$reportId.')');
		    
      // create 1 report for each design that exists
      //$reportId = array();
      //$reportName = array();
      //$Created = 0;
      //foreach (Report::getDesigns() as $design)
      //              {
	  //				  echo('report design:'.$design);
      //                for($i = 1; $i <= 5; $i++)
      //                {
	  //					 $reportName[$design] = $design.'_Test'.$i; 
	  //					 Report::deleteByName($reportName[$design]);
      //                   $reportId[$design] = Report::createReport($reportName[$design], $design);
      //                   $Created++;
      //                  
      //                }
      //                
      //              }
      //           
	  //     
      //      echo('Reports created:'.Delta_Db::$Report->count()); 
      }
	  
	  public function addmeterAction()
	    {
            set_time_limit(1500);    // added after build 2.1.124 to make the script still working as expected.
		    $this->_helper->viewRenderer->setNoRender();
        	    $this->_helper->layout->disableLayout();
				
	        $Parent = $this->getParam('parent');
            $Type = $this->getParam('type');
            $InstanceID = $this->getParam('instance');
			$Name = $this->getParam('name');
			$Order = intval($this->getParam('order'));
			
			$Area = NULL;
			$Meter = NULL;
			
			if ($Type == 'area')
			  {
				$Area = $InstanceID;
			  }
			else
			 {
				$Meter = $InstanceID;
			 }
			 
			$NewMeterNode = Report_Meter::createMeterNode($Parent, $Area, $Meter, $Name, $Order);
			
			echo('<br> NewMeterNode was added ( '.$NewMeterNode.' )');
	  
      }
	  
	  public function createsiteAction()
	    {
            set_time_limit(1500);    // added after build 2.1.124 to make the script still working as expected.
		    $this->_helper->viewRenderer->setNoRender();
        	    $this->_helper->layout->disableLayout();
				
	        $SiteName = 'RV Site';
	        $DeviceNumber = 910801;
	        $TimeZone = '';
	        $SiteAddress = '';
	        $DeviceName = 'DEV_910801';
			Site::CreateSite($SiteName, $DeviceNumber, $TimeZone, $SiteAddress, $DeviceName);
			$Site = Site::getByName($SiteName);
			if ($Site instanceof Site)
			  {
				  $Historian = Settings_Historian::getOneBySite($Site);
				  if ($Historian instanceof Settings_Historian)
                    {
                      $this->Historian->adapter  = 'Mysqli';
                      $this->Historian->host     = 'webteamlinux.deltacontrols.com';
                      $this->Historian->port     = '3306';
                      $this->Historian->dbname   = 'reportverification';
                      $this->Historian->username = 'root';
                      $this->Historian->password = 'xwing';
                    }
                  else
                    {
                      Settings_Historian::insert(
                                           array('Site'     => $Site,
                                                 'adapter'  => 'Mysqli',
                                                 'host'     => 'webteamlinux.deltacontrols.com',
                                                 'port'     => '3306',
                                                 'dbname'   => 'reportverification',
                                                 'username' => 'root',
                                                 'password' => 'xwing')
                                                );
			        }
	  
	  
              }
		}
  }
