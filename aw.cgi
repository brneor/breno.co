#!/usr/bin/perl
# aw.cgi -- the asciiweb site engine
# Version 0.90 20041130
# by Peter A. H. Peterson <pedro@robotfindskitten.org>
# linewrapping code by David Gardner <davidgardner28@gmail.com>
# Thanks to Sam Phillips <sam@dasbistro.com>, Nick Moffitt <nick@zork.net>,
# Neale Pickett <neale@woozle.org>, Stephane <stephane@zork.net>,
# and Sean Neakums <sneakums@zork.net> for assistance, ideas, and advice.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# You may also find it at:
# http://www.gnu.org/licenses/gpl.txt

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser); # sends messages to browser
use Cwd qw(cwd 
	   abs_path); 
use strict;

my $debugmode = 0; # set to one to see debugging information. (Or set the debugmode query parameter.)

my %options; # hash including all run-time program options

# Default critical information in case the user's configs are wrong or absent.
$options{title} = "An unconfigured ASCIIweb site! Check your configurations!";
$options{bgcolor} = "#ffffff";
$options{text} = "#000000";
$options{link} = "#ff0000";
$options{vlink} = "#00ff00";
$options{alink} = "#0000ff";
$options{allowexecute} = 0;
$options{executepage} = 0;
$options{dynamic_debug} = 0;
$options{scriptdir} = "adlkjhasdflkjh";
$options{docdir} = "/var/www/";
$options{header} = "undefined.rfk";
$options{footer} = "undefined.rfk";
$options{main} = "undefined.rfk";
$options{mainfill} = "undefined.rfk";
$options{leftmenu} = "undefined.rfk";
$options{leftfill} = "undefined.rfk";
$options{rightmenu} = "undefined.rfk";
$options{rightfill} = "undefined.rfk";
$options{textwrap} = 1; # disabled here, enabled in aw.conf


# load our defaults into %options
if (-e "aw.conf") {
	open (SITE_DEFAULTS, "aw.conf") or die "I can't open aw.conf! $!";
	while (<SITE_DEFAULTS>) {
		if (/^#/ || /^\s/) { # skip comments and/or whitespace immediately
			next;
		} else { # if key=value pairs exist, add them to the default hash.
			my ($key, $value) = /([^=]+)=([^\n]+)/;
			$options{$key} = $value;
		}
	}
	close (SITE_DEFAULTS);
} else {
	abort("ASCIIweb can't find aw.conf. Check your configurations.");
}

# Debugging Information:
# ----------------------
my @messages; # array for messages to be passed to the browser.
g("Hello, wayward netizen! ASCIIweb is being debugged as we speak -- please pardon the dust!");
	
# CONFIGURATION STUFF:
#---------------------

# load and overwrite any page-specific values in %options.
# this section looks for a foo.rfk.conf file when 'main=foo.rfk', and overwrites the 
# values obtained from aw.conf. Use this to change ascii items and set unique titles for 
# specific pages. (This can be used to create "animations" from one page to another)
# such as depressed buttons or custom header files for individual main documents.

# This process is easy for top level .rfk files, but not for directories.
# If the 'main' parameter points to a directory (ends in or contains /), we look for
# directoryname.conf instead of filename.rfk.conf.  foobar/ yields foobar.conf
# but foo/bar/bash yields foo_bar_bash.conf so that individual sub-directories
# can have special graphics and/or titles.

# It would not be hard to implement configuration information within the rfk files them
# selves, except that such information cannot be included in a directory, as the directory
# isn't a parsed file. I decided to have one configuration method, rather than one for
# rfk files and one for directories. BUt I could be convinced otherwise.

# A final note: while it is possible to acheive this effect by specifying multiple
# pages in the query string, this effect will be lost if the user "compiles" the pages
# statically with gp, as gp only looks at the rfk input file and the conf information.

if (param("main")) { # only do this if we're loading a non-default document in "main"

	my $conffile = param("main"); # we're going to look for a custom file by this name.
	$conffile =~ s#$options{localdir}##; # if it is a fully qualified url, remove the $localdir to get the relative path
	$conffile =~ s#([^/]+)/$#$1#; # remove trailing slash from name for looks (foo_.conf is an ugly filename)
	$conffile =~ s#/#_#g; # replace any other slashes with underscores (foo_bar_bash.conf)
	
	# A user may often *NOT* want to bother creating conf files for every
	# level of a directory, but they want some kind of thing to persist
	# throughout the directory view, such as a custom header announcing the "Images" directory.
	# If there is not a .conf file for that directory, and the user has
	# requested persistent directory confs, we'll see if there are confs
	# at any step along the way and if so, add them together.

	if ($options{persistdirconf} == 1) {
	
		g("Persistently looking through path $conffile...");

		my $pathconf = $conffile;
#		$pathconf =~ s/(.+)_?([^.]+.rfk)(\.conf)/$1/; # ditch any filename and terminal _
		g("My full pathconf before splitting is: $pathconf.");
		my @patharray = split /_/, $pathconf; # 
		my $temp = join ",", @patharray;
		g("My pathconf is $temp and my patharray is " . ($#patharray + 1) . " items long.");

		for (my $i = 0; $i <= $#patharray; $i++) {
			my $pathconf; # let's reuse this variable to construct a recursive conf

			for (my $j = 0; $j <= $i; $j++) {
	
				$pathconf .= $patharray[$j];
				if ($j != $i) {
					$pathconf = $pathconf . "_";
				} else {
					$pathconf .= ".conf";
					$pathconf = $options{'confdir'} . "/" . $pathconf;
				}
			}

			g("pathconf assembled: $pathconf");
			# open $conffile if it exists, read it in and overwrite the defaults.
			get_conf($pathconf);

		}
			
	} else { # we only load ONE conf file for the page.
			$conffile = "$options{confdir}/" . $conffile . ".conf"; # add directory and extension to filename
	
			# open $conffile if it exists, read it in and overwrite the defaults.
			get_conf($conffile);
	}


}

# put the values from %options into easily accessible variables.
# This may be bad form, but I think it's a lot easier than always referring to the hash.
# Maybe I should export everything from the hash and then destroy it... I don't know.

my $script = $options{script}; # the url of this script
my $title = $options{title}; # default title for this site
my $wwwroot = $options{wwwroot}; # the root of this website (vhost/servername)
my $localdir = $options{localdir}; # the directory in which the script resides
my $head = $options{header}; # default ascii-art header
my $leftmenu = $options{leftmenu}; # default left-hand menu
my $leftfill = $options{leftfill}; # default left-hand fill
my $main = $options{main}; # default center (content) page
# I doubt you'll want to change mainfill (typically whitespace), but it is possible. That's the kind of service asciiweb offers.
my $mainfill = $options{mainfill}; # default center fill (probably whitespace)
my $rightmenu = $options{rightmenu}; # default right-hand menu
my $rightfill = $options{rightfill}; # default right-hand fill
my $foot = $options{footer}; # default ascii-art footer
my $rcolwidth = $options{rcolwidth}; # supposed right column width
my $lcolwidth = $options{lcolwidth}; # supposed left column width
my $ccolwidth = $options{ccolwidth}; # supposed center column width
my $bgcolor = $options{bgcolor}; # default background color
my $text = $options{text}; # default body text color
my $readcolor = $options{readcolor}; # default color for main document text for better readability
my $link = $options{link}; # default link color
my $alink = $options{alink}; # default active link color
my $vlink = $options{vlink}; # default visited link color
my $allowexecute = $options{allowexecute}; # (1 or 0) allow scripts to be excecuted BY ASCIIweb.
my $executepage = $options{executepage}; # allow full-page script content. (as opposed to embedded content)
my $scriptdir = $options{scriptdir}; # location all scripts will run from
my $docdir = $options{docdir}; # highest subdirectory that is permissible to read from (i.e. /var/www/)
my $dynamic_debugmode = $options{dynamic_debugmode};
$debugmode = $options{debugmode};
my $textwrap = $options{textwrap};


# And will you be running in static or dynamic mode today?
my $staticmode = 0;
$staticmode = 1 if ($ARGV[0] =~ /(-s|--static)/);  # if invoked with -s, static, or -static, run in static mode.
g("I'll be running in staticmode today, thank you.") if ($staticmode == 1);



if ($staticmode) {

	$main = $ARGV[1]; # the 'main' window content to load.
	g("This is asciiweb run ", time, ". This is a <b>$main</b> train to downtown.");

} else { 
	# We are not going to run in static mode, which means that
	# we are running dynamically and must therefore check the query string.
	
	# If there are any special values in the query string, they override *ALL* other values
	# (except debugmode which is only allowed if $dynamic_debugmode is set in aw.conf).
	
	# Otherwise, we use what is in the aw.conf or filename.rfk.conf file.
	# a clever user could use this with long URLs instead of an rfk.conf file if he/she 
	# wanted. 
	
	# WE ASSUME static users are NOT passing parameters on the query string (I don't think
	# you can do that on the command line anyway), so if a user intends to
	# go back and forth between static and dynamic, they should NOT use
	# such hackery.

# These should not be changeable via the query string because of security issues.
#	if (param("script")) {$script = param("script")};
#	if (param("wwwroot")) {$wwwroot = param("wwwroot")};
#	if (param("localdir")) {$localdir = param("localdir")};
	
	if (param("title")) {$title = param("title")};
	if (param("header")) {$head = param("header")};
	if (param("leftmenu")) {$leftmenu = param("leftmenu")};
	if (param("main")) {$main = param("main")};
	if (param("footer")) {$foot = param("footer")};
	if (param("leftfill")) {$leftfill = param("leftfill")};
	if (param("rightmenu")) {$rightmenu = param("rightmenu")};
	if (param("rightfill")) {$rightfill = param("rightfill")};
	if (param("mainfill")) {$mainfill = param("mainfill")};
	if (param("debugmode") && $dynamic_debugmode) {$debugmode = param("debugmode")};

}

# Obtain all relevant pages for processing and formatting.  &get_page will
# handle finding the pages and any necessary embedding from exec commands, as
# well as processing the URLs contained in those pages depending on how
# staticmode is set. In short, &get_page does all the heavy lifting.

my @HEADER = get_page($head);
my @L_MENU = get_page($leftmenu);
my @CENTER = get_page($main);
my @FOOTER = get_page($foot);
my @L_FILLER = get_page($leftfill);
my @R_MENU = get_page($rightmenu);
my @R_FILLER = get_page($rightfill);
my @C_FILLER = get_page($mainfill);

# Ok. Now that we have all the documents, we can  actually start outputting 
# the page body to the browser.

# give the html type header to the browser if dynamic...
# no header if static, because the server will provide that.
print header() unless $staticmode;


# and set up the page...
print <<END;

<html><head>
<title>$title</title>
</head>
<body bgcolor="$bgcolor" text="$text" link="$link" alink="$alink" vlink="$vlink">

END

# DEBUGGING/INFORMATIONAL MESSAGES:
# the array @messages is intended as a way for the script to print debugging messsages 
# and other non-fatal messages to the user or more likely administrator. If
# there's anything in the array, it will print at the top of the page in the order
# the messages were generated.

if (@messages) {
	print "<p><b>ALERT! ", $#messages + 1, " message(s) exist(s):</b></p>";
	foreach my $foo (@messages) {
		print "<p>$foo</p>\n";
	}
}


print "<pre>"; # let's get down to business

# Print the top of the ASCIIweb page.

foreach (@HEADER) { # the @header doesn't need any special handling or processing,
	print "$_ \n"; # so we just print it at the top of the page.
}

# We need to figure out which column (L, R, or Center) is longest since the
# whole document will need to be formed around the longest column.

my $longest = get_longest(); # This variable holds the length of the longest column.


# PADDING OUT COLUMNS:
# In order to have straight columns, we need to pad out each column to the 
# appropriate width.

# first pad out all center lines out to $ccolwidth -- we will need to do this
# regardless of how long @CENTER is or else our right margin will all be choppy.

# While we're doing this, it is important to see if @CENTER is going to fit 
# inside the predefined column width.

# Thus, we need to find out if @CENTER will fit inside and play nice with @R_MENU.
# We do this by checking the width of each line in a copy of @CENTER, minus any
# HTML, to see if it is longer than $colwidth. 

# We begin by assuming that @CENTER will fit ($plays_well_with_others = 1), but 
# once any single line is too long, we change $plays_well_with_others to 0, 
# which eliminates the @R_MENU for that pagedraw. Otherwise the center 
# column pushes @R_MENU out and it looks bad.

# If a row is shorter than $ccolwidth, we pad the row out to it's full $ccolwidth
# to keep the inside right margin straight.

my $plays_well_with_others = 1;

for (my $j = 0; $j <= $#CENTER; $j++) {
	my $bokbar = get_bokbar ($CENTER[$j]); # don't count HTML as space taking columns...
 	if (length($bokbar) > $ccolwidth) {
		if ($textwrap) {
			wrap_line ($ccolwidth, $j);
			$bokbar = get_bokbar ($CENTER[$j]);
		} else {
			# @CENTER is too big for it's britches. R_MENU will not be displayed.
 			$plays_well_with_others = 0; 
		}
 	} 
 		
	#moved from else, if we did line_wrap then we still want padding
	if ($plays_well_with_others == 1) {	
		for (my $blanks = length($bokbar); $blanks < $ccolwidth; $blanks++) {
 			$CENTER[$j] = $CENTER[$j] . " "; # fill out the end of the line with spaces.
 		}
	}
} # end row padding / width check section. 

#re-calculate longest if we did any textwrapping
if ($textwrap) {
  $longest=get_longest();
}

# FILLER FILES:
# -------------
# There are also three "filler" files -- left, center, and right. These files contain 
# the data that will fill empty space in a column. For example, If the center column (main)
# is longer than either the l_menu or r_menu, l_filler and r_filler will make up the empty 
# space.

# fill the @L_MENU column with the @L_FILLER file if it is shorter than the others.

my $deficit; # number of rows we need to add to short columns.

$deficit = $longest - $#L_MENU;

if ($deficit > 0) {
	my $fill_line = 0;
	for (my $line_no = $#L_MENU + 1; $line_no <= $longest; $line_no++) {
		$L_MENU[$line_no] = $L_FILLER[$fill_line]; # add filler to current line
		$fill_line++;                              # incremement filler line count
		if ($fill_line == ($#L_FILLER + 1)) {
			 $fill_line = 0;
		} # if at the end of filler file, repeat.
		for (my $blanks = length($L_MENU[$line_no]); $blanks < $lcolwidth; $blanks++) {
		   	$L_MENU[$line_no] = $L_MENU[$line_no] . " "; # fill in the space left by the not-wide-enough filler.
		} # end blank fill
	} # end $line_no fill
} # end filling routine

# fill @CENTER with @C_FILLER (which is probably a blank line) if it is short.

$deficit = $longest - $#CENTER;

if ($deficit > 0) {
	my $fill_line = 0;
	for (my $line_no = $#CENTER + 1; $line_no <= $longest; $line_no++) {
		$CENTER[$line_no] = $C_FILLER[$fill_line]; # add filler to current line
		$fill_line++;                              # incremement filler line count
		if ($fill_line == ($#C_FILLER + 1)) {
			$fill_line = 0;
		} # if at the end of filler file, repeat.
	} # end $line_no ascii fill
} # end filling routine

# fill @R_MENU with @R_FILLER if it is short...

$deficit = $longest - $#R_MENU;

if ($deficit > 0) {
	my $fill_line = 0;
	for (my $line_no = $#R_MENU + 1; $line_no <= $longest; $line_no++) {
		 $R_MENU[$line_no] = $R_FILLER[$fill_line]; # add filler to current line
		 $fill_line++;                              # incremement filler line count
		 if ($fill_line == ($#R_FILLER + 1)) {
			 $fill_line = 0;
		 } # if at the end of filler file, repeat.
		 for (my $blanks = length($R_MENU[$line_no]); $blanks < $rcolwidth; $blanks++) {
		   	$R_MENU[$line_no] = $R_MENU[$line_no] . " "; # fill in the space left by the not-wide-enough filler.
		 } # end blank fill
	} # end $line_no fill
} # end filling routine


# ASSEMBLING THE COLUMNS:
# -----------------------

# since we know our columns are all the same length and are the appropriate
# widths (that's what we've been doing all this time), we don't have to do any
# fancy mucking about -- lets just output the columns one line at a time!

# READCOLOR: if $readcolor exists, paint @CENTER in that color to help bring 
# it out of the background. If $readcolor is undefined, skip the $readcolor 
# font tags.

for (my $j = 0; $j <= $longest; $j++) {
	
	my $one = $L_MENU[$j];
	my $two = $CENTER[$j];
	my $three = $R_MENU[$j]; 
	chomp ($one, $two);

	if ($plays_well_with_others == 0) { # if @CENTER is too wide to fit inside, skip the right hand column.
		print "$one ";
		print "<font color='$readcolor'>" if $readcolor;
		print "$two";
		print "</font>" if $readcolor;
		print "\n"; # notice the lack of a right hand column
	} else {
		print "$one ";
		print "<font color='$readcolor'>" if $readcolor;
		print "$two";
		print "</font>" if $readcolor;
		print " $three\n"; # all three columns displayed
	}
} # next line, please

# Print the document footer -- no fuss, no muss.

foreach (@FOOTER) { # print the footer just like the header, no fancy stuff here
	print "$_ \n";
}

print "</pre>"; # done with the output

print end_html();

# SUBROUTINES!
# ------------
# This is where all the fancy stuff happens.

sub wrap_line { # arguments: $width, $j
# Wraps text in lines in center collumn that are too long. Also we can't use
# rindex because we need to not count html tags as part of the width.
# The basic logic for this is:
# 1) find the last whitespace before width
# 2) if found split the string at this point and append the stuff on the right to 
#    the front of next_line
# 3) else do a hard break at width 

  if ($options{textwrap} < 1) {
	  g("textwrap is set to '$options{textwrap}'");
  }
	  
	
  (my $width, my $j) = @_;
  my $last_whitespc = -1; 
  my $tag_start = 0; # handleing wrapping of links the idea is to preserve the
  my $tag_stop = 0;  # original <a href> tag, add a </a> to the end of $cur_line
  my $in_link = 0;   # and then duplicate the href at the front of $next_line
  my $tag;
  my $length = 0; 
  my $cur_line = $CENTER[$j];
  my $next_line = "";
  my @line = split(//,$cur_line);
  my $break_point;
  
  if ($width > length($cur_line)) { # sanity check
	#uhoh calling code made an error
	die "wrap_line called with bad arguments";
  }

  for (my $k=0; $length < $width; $k++) {
	if ($line[$k] eq "<") { # inside tag
		$tag_start = $k;
		while ($k <= $#line && $line[$k] ne ">") {$k++;}
		$tag_stop = $k;
	
		#save tag we may need it for later
		$tag = substr ($cur_line, $tag_start, $tag_stop-$tag_start+1);
		if ($in_link && $tag =~ /\/a/) {
			$in_link = 0;
		} elsif ($tag =~ /a href/) {
			$in_link = 1;
		}
	} else {
		$length++;
		if ($line[$k] =~ /\s/) {
			$last_whitespc=$k;
		}elsif ($line[$k] eq "&") { #kinda a hack skip till we find ";" 
                       	while ($k <= $#line && $line[$k] ne ";") {$k++;}
		}
	}
  }
  

  if ($last_whitespc < 0) {
  	$next_line = substr($cur_line, $width);
  	$cur_line =  substr($cur_line, 0, $width);
  } else {
  	$next_line = substr($cur_line, $last_whitespc +1);
  	$cur_line =  substr($cur_line, 0, $last_whitespc);
  }

  if ($in_link) {
	$cur_line = $cur_line . "</a>";
	$next_line = $tag . $next_line;
  }

  $CENTER[$j] = $cur_line;

  if ($j == $#CENTER) { # if we are at the end
	push(@CENTER, $next_line);
  } elsif ($CENTER[$j+1] !~ /\S/) { # if next line is blank, then insert a line
	splice (@CENTER, $j+1, 1, $next_line, " ");	
  } else {
	$CENTER[$j+1] = $next_line . " " . $CENTER[$j+1];
  }
} # end wrap_line

sub get_bokbar {
  my $bokbar = $_[0]; # don't count HTML as space taking columns...
  $bokbar =~ s/<[^>]+>//ig; # remove all html for column counting, since html tags are "invisible".
  $bokbar =~ s/&\w+;/X/ig; # replace html escape sequences with one character for counting since they appear as one character.
  return $bokbar;
} # end get_bokbar

sub get_longest { #with text wrapping we are increasing the lenght and will need to re-compute
  my $longest;
  if ($#L_MENU >= $#CENTER && $#L_MENU >= $#R_MENU){
    $longest = $#L_MENU;
  }elsif ($#CENTER >= $#L_MENU && $#CENTER >= $#R_MENU) {
    $longest = $#CENTER;
  }else{
    $longest = $#R_MENU;
  }
  return $longest;
} # end get_longest

sub get_page {
# get_page does most of the complicated work. It gets the page, 
# cleans up the urls, embeds any scripts called, and spits the output back to
# the script for processing. This is what actually makes dynamic asciiweb work,
# because it takes "live HTML" and changes it so that it works in the context
# of a script like this.

# the variable that will hold that data
my $data;

# I did not indent this subroutine because it is so long.

# the page location we are retrieving and processing
my $current_url = $_[0];

# Get rid of any trailing nonprintables. Once upon a time, this was an 
# extremely frustrating bug.
chomp($current_url);

# we need a "directory url" (called current_dir) for this page item so that we
# can reassemble paths and determine if a file is local (and/or if includes are
# allowed). If the end of the URL is a slash, we dont' need to chop it at all
# (because there is no filename). If it ends with a filename, we chop off the
# filename portion. 
if ($current_url eq "") {

	die "current_url cannot be empty.";
}
g("current_url is: $current_url");
my $current_dir = $current_url;
unless ($current_dir =~ /\/$/) {
       $current_dir =~ s/([^\/]*$)//i;
}
g("Generated current_dir: $current_dir");

# files in the 'dressing' directory are only there to keep them out of the docdir
# so that the / doesn't get full of little window dressing files. It also provides a 
# place for dressing files to go so that they don' have to be relative to the page
# in the 'main' pane. If current_dir is http://robotfindskitten.org/dressing/,
# just make it http://robotfindskitten.org/ so that relative linking from
# dressing files works the way you expect it to.
if ($current_dir =~ s/$options{'dressing'}//) {
       if ($current_dir eq "/") {
       	   $current_dir = "";
	   # if after removing the dressing dir, all you have is /, remove that too.
       }
       g("Amended current_dir: $current_dir (dressing dir removed)");
} else {
	g("No dressing dir found.");
}

g("current_dir: $current_dir");

# SECURITY TESTS FOR THE MAIN PARAMETER:
# --------------------------------------

# OK. Now we're all set to go and get the actual page.
# If we can get this page from the filesystem instead of LWP, let's do that!
# Getting files from the filesystem instead of the webserver provides close to 
# a 100% speedup for an average file.

# Checking for docdir: using the abs_path function we'll check for the absolute
# path of the file $current_url and verify that docdir is the first part of the 
# absolute path. If it does not match docdir, we will not load it locally, nor
# will we allow executes, instead attempting to load the path (which is probably 
# bogus) via LWP.


g("Trying to get absolute path for $current_url");
my $abs_path = $current_url;
$abs_path =~ s/^$localdir//;
$abs_path =~ s/^\///;
$abs_path = abs_path($abs_path);
g("Absolute path: $abs_path");

my $pagescript;
if ($current_url =~ m/exec:(.+)/) {
	$pagescript = $current_url;
	$pagescript =~ s/exec:(.+)/$1/;
	g(abs_path("$scriptdir/$pagescript"));
	g("abs_path for $pagescript : ". abs_path("$scriptdir/$pagescript"));
	g("source should be: $docdir$scriptdir ");
	if (abs_path("$scriptdir/$pagescript") =~ /^$docdir$scriptdir\/.+/) {
		g("Exec script is in scriptdir.");
		
	} else {
	
		g("Exec script is not in scriptdir.");
	}
		
}



if (-f $abs_path && $abs_path =~ /^$docdir/ && $abs_path !~ /^$docdir$scriptdir/ && $abs_path !~ /exec:/) {
#if (-f $docdir . $current_url) {

	g("I found and am loading $abs_path from the filesystem!");
#	push @messages, "I am loading $docdir$current_url from the filesystem!" if $debugmode;
	
	open PAGE, $abs_path;
	local $/ = undef; # clear record separator for this block.
	$data = <PAGE>; # slurp in one big chunk, thanks to $/ not being \n. Thanks Sriram!
	close PAGE;
	
	# CHECKING FOR <exec="foo.pl"> COMMANDS WITHIN THE TEXT:
	# as a limited security measure, ASCIIweb will only search for execution commands
	# in files it has obtained locally (or is explicitly told to execute locally).
	# we now scan our locally obtained $data for any execution commands and if so, 
	# replace the execution tag with the data received by executing it.

	while ($data =~ /<exec="([^"]+)">/ && $allowexecute) {
	g("Hey, I found a script called $1! I'll try to merge it into this page!");
		open OUTPUT, "$scriptdir/$1 |" or die "ASCIIweb can't execute $1 from inside an rfk file!\nThis is ostensibly because: $!\n";
		my $script_output; # where our snippet will be placed.
		local $/ = undef; # clear record separator for this block.
		$script_output = <OUTPUT>; # slurp in one big chunk, thanks to $/ not being \n. Thanks Sriram
		close OUTPUT;

		$data =~ s/<exec="[^"]+">/$script_output/;
	}
		
# EXECUTING *FULL-PAGE* INCLUDES:	
# this looks for aw.cgi?main=exec:foo.pl and if script execution AND executepage 
# are enabled, attempts to run the script. It also requires executepage set to 1,
# because this makes the script name visible in the query string, and this could
# constitute a security hazard.

} elsif ( $allowexecute && $executepage && $current_url =~ /exec:(.+)/ && abs_path("$scriptdir/$1") =~ /^$docdir$scriptdir/) {

	my $script = $current_url;
	$script =~ s/exec:(.+)/$1/;
#	die ("Attempting to load full-page include $current_url as $script.");
	
	g("Loading full page include $scriptdir/$script.");
	
	open OUTPUT, "$scriptdir/$script |" or die "ASCIIweb can't execute $script directly!\nThis is supposedly because: $!\n";
	local $/ = undef; # clear record separator for this block.
	$data = <OUTPUT>; # slurp in one big chunk, thanks to $/ not being \n. Thanks Sriram
	close OUTPUT;
	
} elsif ($current_url !~ /$scriptdir/) { 

	# get the page via LWP since we can't seem to get it locally...

	# For security purposes, we will not get a url that contains the name of your
	# local scriptdir (so that viewers cannot see your module source code),
	# so it pays to name your scriptdir something random and uncommon.
	
	# This method is slower and creates load on the web server!
	g("I am loading $current_url via HTTP.");

	my $qualified_url = qualify_url($current_url);	# See &qualify_url.

	# use LWP to get the pages and store them in $data.
	# Create a user agent object
	use LWP::UserAgent;
	my $ua = new LWP::UserAgent;
	$ua->agent("AgentName/0.1 " . $ua->agent);
	# Create a request
	my $req = new HTTP::Request GET => $qualified_url;
	# Pass request to the user agent
	my $page = $ua->request($req);
	
	$data = $page->content;
} else {

	# This event is triggered if a person attempts to view any URL where
	# any part of that URL matches your scriptdir. This helps keep prying
	# eyes out of your potentially insecure modules. The message is
	# intentionally obscure so as to not give potential attackers any help.

	# PLEASE set an appropriate .htaccess file with the line "Options-Indexes"
	# in your scriptdir to keep people from directly accessing it with a URL
	# that avoids asciiweb altogether.

	g("I am loading $current_url via HTTP.");

	# uncomment the next line if you want to know when this occurs (but please
	# for your sake re-comment it afterwards):

	# push @messages, "Ok, Ok! I deliberately avoided $current_url because it matched $scriptdir. Now please go re-comment this line in the sourcecode already." if $debugmode;
}

# MISSING SOME EXEC TAGS?
# Uncomment this code if you think executes are not working properly. If you're happy, why waste the cycles?
if ($data =~ /<exec="([^"]+)">/) {

	g("I spotted an exec command for $1 but didn't do it. Perhaps it was not a local file. FYI, allowexecute is set to $allowexecute.");

}


# Now that we've picked up the file (either locally or via the web), 
#we need to qualify the URL for context later.
$current_url = qualify_url($current_url);
g("current_url: $current_url");

# now for the fun part!
# Since we now have a whole web page in the value of $data, we can do 
# stuff to it (particularly on the HTML in it) in order to make the
# pages into a format that is useful for us.

# GETTING USEFUL INFORMATION FROM A URL: 
# Depending on what we want to do, we need to have some different variables on
# hand with different portions of the URL stored for easy access, like the base
# url, the filename, things like that.

# when dealing with "full path relative links" like "/~pedro/" (i.e. the
# top-level "Parent Directory" link in an HTML directory) we need the basest of
# URLs -- so http://foo.bar/bash/zubaz.html becomes http://foo.bar
	
	my $server_url = $current_url;
		$server_url =~ s/(http:\/\/[^\/]+)\/.*/$1/i;
g("server_url: $server_url");

# HTML directory sorting features happen by passing the server parameters after
# the directory's URL. In order to allow sorting by different criterias, we
# need to chop off the query string so that next time we can get a new query
# string.

	my $current_url_plain = $current_url;
		$current_url_plain =~ s/(http:\/\/.+)\/+\?.+/$1/i;

g("current_url_plain: $current_url_plain");


# DYNAMIC OR STATIC?
# If we are making dynamic pages, we have to process URLs differently
# than if we are making static pages. 

# WARNING: Staticmode does not look at anything in the query string
# EXCEPT the main parameter. If you want to use funky effects, describe
# them in a page-specific conf file. Because you may view an rfk file from
# any referring page, and each of those query strings could specify other ASCII
# elements, it is not practical to spider for and create all these different
# pages.

if ($staticmode) { # if we are generating static pages
	
	# If main is a full hyperlink to a file, discard everything but the url in i
	# the main parameter.
	$data =~ s/(<a href=")($script|aw\.cgi)\?main=(http:[^&"]+)([^>]+>)/$1$3">/ig;

	if ($current_dir eq "./" || $current_dir eq "/" || $current_dir eq "") {
		$current_dir = $localdir;
		g("Top level current dir replaced with: $current_dir");
	}


	# RELATIVE LINKS:
	# example: <a href="shots.rfk">
	# becomes: <a href="shots.html">
	$data  =~ s/(<a href=")(?!http:\/\/)([^.]+\.)(rfk|html)("[^>]*>)/$1$current_dir$2html$4/ig;

	# RELATIVE LINKS that include LOCAL PATHS:

	$data =~ s/(<a href=")[^=]+=([^&"]+)[^"]*[^>]*>/$1$localdir$2">/ig;

	# YOU FORGOT TO REMOVE REFERENCES TO AW.CGI, DIDN'T YOU?
	# if a url contains aw.cgi?... remove the reference to the script and replace
	# with the contents of the main parameter. Also, if the parameter is an .rfk page,
	# change the file extension to .html. A user may do this so that they can 
	# seamlessly switch between static and dynamic page generation.

	# example: <a href="aw.cgi?main=barf.rfk">
	# becomes: <a href="barf.html">

##	$data =~ s/(<a href="http:\/\/tastytronic.net\/asciiweb\/test\/)(aw\.cgi\?)(main=[^&]+)([^"]*)("[^>]*>)/$1$3$5/ig; 
##	$data =~ s/(<a href="[^?]+\?)main=([^&"]?)(&[^"]+)?("[^>]*>)/$1$localdir$2$4/ig;

	$data =~ s/\.rfk("[^>]*>)/\.html$1/ig;

	# We leave all other URLs alone, because static mode is boring.
	

} else { # if not we are running in dynamic mode

# HTML CLEANUP
# ------------
# This will run differently for a few different
# cases -- if the page is foo.html, we expect it to be normal HTML and
# know that there are certain things we want to do to it. Likewise, if
# the URL ends with a slash, like foo/ we understand that we want to 
# treat it as web directory. (So don't point it to foo/ if you mean 
# foo/index.html) The final type is foo.rfk, which is the standard file
# format for asciiweb, which utilizes certain tags that the script 
# understands. We don't need to clean the urls on an .rfk file, since
# the author of the .rfk wouldn't have used these nasty tags that we 
# don't support.
#
# We only have to do this to make real .html pages presentable in asciiweb,
# so most of the time we'll be skipping this part of the program.

# First, we change the HTML tags that we like and want to use.

#unless ($current_url =~ /.+\.rfk$/) { # do this block UNLESS it ends in .rfk
if ($data =~ /<html>/i) { # do this block -- it thinks it's HTML!
	g("I am treating this page as HTML and processing some tags.");

	$data  =~ s/<\/p.*>/\n\n/ig; # replace closing paragraphs with 2x newline
	$data  =~ s/<br>/\n/ig; # replace line breaks with 1x newline
	$data  =~ s/<LI>/\*  /ig; # poor man's bullet
	$data  =~ s/<(\/?)h[1-6]>/<$1B>/ig; # make any headers bold text
	$data  =~ s/\t/     /ig; # tabs should be spaces
	$data  =~ s/<hr[^>]*>/-----------------------------------------/ig; # poor man's horizontal rule
	$data  =~ s/<dd>([^<]*)<\/dd>/$1\n/ig;
	$data  =~ s/<dt>([^>]*)<\/dt>/<b>$1<\/b>\n/ig;

	# this is the monster regex that parses HTML pages. All these tags
	# and *sometimes* their contents (like <title>foo</title>) are 
	# being thrown away since we don't need them.
	
	$data  =~ s/(<\/?dt>|<\/?tt>|<\/?dl>|<\/?center>|<\/?blockquote>|<\/?dd>|<img[^>]*>|<link[^>]*>|<\/?pre>|<\/?html[^>]*>|<\/?head[^>]*>|<\/?address[^>]*>|<!--[^>]*>|<\/?body[^>]*>|<meta[^>]*>|<title[^>]*>[^<]*<\/title>|<p[^>]*>|<\/?ul>|<\/li>|<\/?TABLE[^>]*>|<\/?TD[^>]*>|<\/?TR[^>]*>|<\/?font[^>]*>|<\!doctype[^>]*>|<\?xml[^>]*>)//ig; # whoa baby

	# sometimes we have whitespace between html tags. this 
	# is useless and annoying.

	#$data  =~ s/>\s*</></ig; # not sure why this is commented out

	# sometimes we have whitespace at the beginning that the 
	# pretags don't like. So let's get rid of all beginning
	# whitespace.
		
	$data  =~ s/^\s+//ig;

} # end of .html-ONLY cleanup.
	
	#  _   _ ____  _       _____ _    ____ _____ ___  ______   __
	# | | | |  _ \| |     |  ___/ \  / ___|_   _/ _ \|  _ \ \ / /
	# | | | | |_) | |     | |_ / _ \| |     | || | | | |_) \ V / 
	# | |_| |  _ <| |___  |  _/ ___ \ |___  | || |_| |  _ < | |  
	#  \___/|_| \_\_____| |_|/_/   \_\____| |_| \___/|_| \_\|_| 
	#        "Choppa Choppa Chop Sockeeeeeeey!" -- Mr. Bad

	# the url factory:
	
	# This is where all the dynamic URL magic happens. All URLs are checked or
	# processed to do what we want. Sometimes that means leaving them alone,
	# sometimes that means feeding them back through asciiweb, etc. This is also
	# why we DON'T do this to static pages.
	
	# The URLs' values have to be changed to act the way the user
	# expects them to, given the illusion of a frameset. This is so
	# that the page author doesn't have to keep track of query strings
	# and so that outside HTML pages can be loaded into the frames
	# even if they weren't intended to be included in an asciiwebpage.
	
	# RELATIVE LINKS
	# if a url found in the page DOES NOT start with http:// but ends with .html,
	# .rfk or / assume that it is the relative URL for a web page that we want to
	# parse and look at within asciiweb. Feed it back into asciiweb and attach
	# $localdir to it. This way, when the link is clicked, that location becomes
	# the new content for the page.

	# the (?!...) is a "negative lookahead assertion" which basically says
	# if this matches INCLUDING NOT having this in this location! In this case,
	# it matches a URL that does not start with http:// -- and hence is local.
	
	# example: <a href="shots.rfk">
	# becomes: <a href="http://foo.bar/aw.cgi?main=http://foo.bar/shots.rfk">
#	$data  =~ s/(<a href=")(?!http:\/\/)([^.]+\.)(rfk|html)("[^>]*>)/$1$script\?main=$current_dir$2$3$4/ig;
	$data  =~ s/(<a href=")(?!http:\/\/)([^.]+\.)(rfk|html)("[^>]*>)/$1$script\?main=$current_dir$2$3$4/ig;
	
	# LIVE APACHE DIRECTORIES
	# -----------------------
	
	# TOP LEVEL "PARENT DIRECTORY" LINKS
	# if the url is just a /, then it's a top-level "Parent Directory" link, which
	# asciiweb recklessly assumes is the top of your asciiweb installation.  (It's
	# very self-absorbed that way.) The proper behavior would be to get you back to
	# wherever you WERE, and not just go to the default "index.rfk" page. This
	# would probably require keeping track of how you got to the directory though,
	# which would be a pain and perhaps beyond the scope of asciiweb.
	
	$data  =~ s/(<a href=")\/("[^>]*>)/$1$script$2/ig; 
	
	# ODDBALL "PARENT DIRECTORY" LINKS
	# in an HTML Index, the "parent directory" link is an oddball, because it 
	# is a quasi-relative link. It's direct from the base URL of the site, but not
	# relative to the current page. So we have to treat "/foo/" URLs differently 
	# from "foo/" URLs.
	
	# example: <a href="/~pedro/pix/">
	# becomes: <a href="http://foo.bar/aw.cgi?main=http://foo.bar/~pedro/pix/">
	$data =~ s/(<a href=")(\/.+\/"[^>]*>)/$1$script\?main=$server_url$2/ig;
	
	# FIXING RELATIVE LINKS IN APACHE DIRECTORIES
	# In an HTML Index, sub-directories appear as a relative link from that
	# subdirectory. This means that while the link to the index will work, 
	# a la ...?main=foo/ the next link downwards won't, since it will try to 
	# be ...?main=bar/ even though the directory bar is below foo and is
	# not relative to asciiweb. So we have to fix that by adding in the 
	# current working directory to URLs that fit that pattern so that they
	# become relative to asciiweb.
	
	# example: for a relative link to directory foo/bokbar/ <a href="bokbar/">
	# becomes: <a href="http://foo.bar/asciiweb.pl?main=currentdir/bokbar/">
	
	$data  =~ s/(<a href=")(?!http:\/\/)([^\/]+\/)("[^>]*>)/$1$script\?main=$current_dir$2$3/ig;
	
	# FIXING RELATIVE LINKS TO RFK/HTML IN APACHE DIRECTORIES
	# In an Apache index, files (like subdirectories) appear as relative links. They
	# must be fully qualified from their current location in order to be displayed
	# properly.
	
	$data  =~ s/(<a href=")(?!http:\/\/)([^.]+\.)(rfk)("[^>]*>)/$1$script\?main=$current_dir$2$3$4/ig;
	
	# SORTING OPTIONS IN APACHE DIRECTORIES
	# if the URL ends in "?\w=\w" we assume it's for an apache HTML 
	# directory and pass it to the server appropriately. This is kind of 
	# crufty, but it works.
	
	$data =~ s/(<a href=")(?!http:\/\/)(\?\w=\w">)/$1$script\?main=$current_url_plain\/$2/ig;
	
	
	# LOOKING AT PICTURES, DOWNLOADING FILES
	# --------------------------------------------------------
	# if the file IS LOCAL and  ends with .png, .jpg, or .tar.gz, etc. qualify it
	# and leave it alone (don't put it back through asciiweb) so that we can see
	# pictures and download tarballs outside of asciiweb. The (?!rfk|html|htm) is
	# a negative lookahead assertion which basically says, "if this matches including
	# NOT having rfk, html, or htm in this position, then go for it." Negative look-
	# aheads are WEIRD.
	
	# example: <a href="foo.jpg"> (in hypothetical directory dumont)
	# becomes: <a href="http://foo.bar/dumont/foo.jpg">
	
	$data =~ s/(<a href=")(?!http:\/\/)(?!#[^"]+")(?![^"]+\.(rfk|html|htm)")([^"]+"[^>]*>)/$1$current_dir$3/ig;
#	$data =~ s/(<a href=")(?!http:\/\/)(?![^"]+(\.rfk|\.html|\.htm|\/)")([^"]+"[^>]*>)/$1$current_dir$3/ig;
	
	
#	...the old and probably much faster way...
#	$data =~ s/(<a href=")(?!http:\/\/)([^"]+(\.(png|jpg|gz|zip|tar\.gz|tar|txt|lha|arj|tgz|bz2|tar\.bz2|deb|rpm))"[^>]*>)/$1$current_dir$2/ig;
	
	# REMOTE FILES THAT WE WANT TO VIEW
	# if the file is remote and meets these qualifications, just pass it
	# along directly to the web client, don't stuff it into 'main'.
	
	$data  =~ s/(<a href=")(.+(\.(png|jpg|zip|gz|txt|tar))"[^>]*>)/$1$2/ig;
	
	# WEIRD STUFF
	# -----------
	
	# A KLUDGE
	# This is sort of kludgey -- but if after all this hootenanny the 'main'
	# parameter ends up with a value equivalent to  $script, we should just send it
	# to "$script", rather than put "$script?main=$script" and get some nasty
	# nesting going on.  In other words, if we find out that the script is trying
	# to look at itself, we just tell it to belch and start over.
	
	$data =~ s/(\??)(&?main=$localdir)\/*(")/$1$3/ig;

	}

# Split $data on linebreaks and put it into @pagearray so that it will zip up 
# like it's supposed to when it gets back to the main function.
my @pagearray = split (/\n/, $data);

} # end get_page

sub qualify_url {
# If the URL is not fully-qualified, add the $localdir scalar to it, ie.
# the url "foo/bar/" becomes "http://local.dir/foo/bar/"
# qualify_url takes in a parameter and if it doesn't start with http:// we
# assume that it is a relative link from the main page and add the local
# http://foo.bar to the relative path. 

# ASCIIweb itself does not traverse the filesystem, so We need this information
# to understand context for further pages which may be relatively linked from
# this (or future) page(s).

	my $url = $_[0];
	if ($url || $localdir) {
		 unless ($url =~ /^http:/) { 
			$url = $localdir . $url;
			}
	} else {
		abort("ASCIIweb was asked to load a null URL.");
	}
	return $url;
}


sub abort {
# &abort terminates asciiweb with a (hopefully useful) error message. In thise
# case, something has gone wrong, even though asciiweb compiled properly.

my $errmsg = $_[0];

print header();
print start_html();
print p("ASCIIweb terminated prematurely with a message:");
print p("$errmsg");
print end_html();
exit;
}

sub get_conf {

	my $conffile = $_[0];

	if (-e $conffile) {
		g("I found  $conffile!");
		open (CUSTOM_CONF, $conffile) || die "Can't open conf file -- check permissions! $!";
		while (<CUSTOM_CONF>) {
			if (/^#/ || /^\s/) { # skip comments and/or whitespace immediately
				next;
			} else { # if key=value pairs exist, add/replace them in the default hash.
				my ($key, $value) = /([^=]+)=([^\n]+)/;
				$options{$key} = $value;
			}
		}
	}
	g("$conffile integrated.");
	
}

sub g {

	my $message = $_[0];
	if ($debugmode) {
		push @messages, $message;
	}
}

