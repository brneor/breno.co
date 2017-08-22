#!/usr/bin/perl -w

# gp -- GenPage -- for generating static ASCIIweb pages

use strict;
use Getopt::Long;

Getopt::Long::Configure ("bundling"); # turn on parameter bundling
				      # and case sensitivity for single letter options

my %opts;

GetOptions (\%opts, 'f|full', 'i|interactive', 'IF=s', 'OF=s', 'v|verbose', 'd|debug');
				      
my $debugmode = 0;
my $fullmode = 0;
my $single = 0;
my $interactive = 0;
my $verbose = 0;
my $if;
my $of;
my $i;

if ($opts{'d'}) {
	foreach (@ARGV) {
	print "$_\n";
	
	}
}
	
if ($opts{'d'}) {
	$debugmode = 1;
	$verbose = 1;
	print "Found -d, welcome to debugmode! (implies verbose)\n" if $debugmode;
} 

if ($opts{'f'}) {
	$fullmode = 1;
	print "Found -f, running in fullmode\n" if $debugmode;
} 
		
if ($opts{'i'}) {
	$interactive = 1;
	$verbose = 1;
	print "Found -i, running in interactive mode (implies verbose)\n" if $debugmode;
} 
		
if ($opts{'v'}) {
	$verbose = 1;
	print "Found -v, running in verbose mode\n" if $debugmode;
	
} 

if ($opts{'IF'}) {
	print "Found -IF switch (implies single)...\n" if $debugmode;
	$if = $opts{'IF'};
	print "...and an argument, '", $opts{'IF'}, "', for it.\n" if $debugmode;
	$single = 1;
	$i++;
			
} 
	
if ($opts{'OF'}) {
	print "Found -OF switch (implies single)...\n" if $debugmode;
	$of = $opts{'OF'};
	print "...and an argument, '", $opts{'OF'}, "', for it.\n" if $debugmode;
	$single = 1;
	$i++;
}
	
if ($ARGV[0]) {
	$if = $ARGV[0];
	$single = 1;
	print "Trying to run with input file $if\n" if $debugmode;
}
	

print "Verbose mode enabled.\n\n" if ($verbose);
print "Interactive mode enabled. Hit \"g\" to leave interactive mode.\n\n" if ($interactive);

if ($single && $fullmode) { # user specified filename AND -f

	$fullmode = 0; # resetting fullmode for safety.
	print "Warning: Parameter conflict: fullmode AND singlemode set.\nFailing to single mode.\n\n";
	cont();
}

if ($fullmode) {

	fullmode();

} elsif ($single) {

	single();

} else {

	print "No input files found.\n\n" if ($verbose);
	help();
 
}

print "Thank you for choosing asciiweb.\n\n"  if ($verbose);
exit 0;

sub cont {
	
	if ($interactive == 0) {
		return 0;
	}
	
	print "Continue with operation? (Y/n/q/g): ";
	my $response = <STDIN>;

	if ($response eq "\n" || $response =~ /[Yy]\n/) {
		return 0;
	} elsif ($response =~ /[Nn]\n/) {
		return 1;
	} elsif ($response =~ /[Gg]\n/) {
		$interactive = 0;
		return 0;
	} elsif ($response =~ /[Qq]\n/) {
		print "Aborting at user command.\n";
		exit 0;
	} else {
		cont();
	}

}

sub genpage {

	my $zubba;

	print "Input file: $_[0], Output file: $_[1]\n"  if ($verbose);
	
        my $result = cont();	
	if ( $result == 0) {
		print "Executing aw.cgi...\n"  if ($verbose);
		$zubba = `perl aw.cgi -s $_[0]`;

		#print "$zubba\n";

		open (FILEWRITE, "> $_[1]") or die "Can't open $_[1] for writing: $!\n";
		print "Writing $_[1]... "  if ($verbose);

		print FILEWRITE $zubba;
		print " $_[1] written.\n\n"  if ($verbose);
		print "." if ($fullmode && !($verbose));
	} elsif ( $result == 1 ) {
		print "\nSkipping $_[0]...\n\n";
	}
	
}

sub single {

	if ($if) {

	#	if ($if =~ /html$/) { # in case they gave an html as the "source" file (a la 404)
	#		$if =~ s/html$/rfk/i;
	#	}

		$if =~ s/\..+$/\.rfk/i; # no matter what they say, the if ends in rfk

		if ($if && !($of)) { # if no of is given, we make one up.
		
			$of = $if;
			$of =~ s/rfk$/html/i;
			print "No output file given, assumed '$of'.";
		}
	
		genpage($if, $of);
		print "\n" unless ($verbose);	
		print "Page generation compleat.\n\n";

	} elsif ($of) { # we have an of, but no if... odd... let's guess at an if.
		
		$of =~ s/\..+$/\.html/i; # no matter how they smell, of ends html
		$if = $of;
		$if =~ s/\..+$/\.rfk/i; # no matter what they say, the if ends in rfk
		print "No input file given, assumed '$if'.";
	
		genpage($if, $of);
		print "\n" unless ($verbose);
		print "Page generation compleat.\n\n";
	}	

	unless ($if || $of) { # somehow get got to single mode without a filename!

		print "Parameter error!\n\n";
		help();
	
	}

}

sub fullmode {

	my @filelist = `find . -name "*.rfk"`;
	my @newlist;
	my $of;

	foreach (@filelist) {
	
		# do not process any .rfk files in the src directory.
		unless ($_ =~ /^\.\/src/ ) {
			push @newlist, $_; # add it to array
		}
	}	

	print "I found these ", ($#newlist + 1), " rfk files to process:\n@newlist\n" if ($verbose);

        if (cont()) {
		print "Aborting at user command.\n";
		exit 0;
	}

	print "Generating ", ($#newlist + 1), " pages...\n";

	foreach (@newlist) {	
	
		chomp $_;
	
		$of = $_;
		$of =~ s/rfk$/html/i;
		genpage($_, $of);
	}
	print "\n" unless ($verbose);

	print "Page generation compleat.\n\n";

}

sub help {


	print "gp -- asciiweb page generator\n";
	print "version 0.50 ALPHA! USE AT YOUR OWN RISK!\n";
	print "-----------------------------------------\n\n";
	print "usage: gp [options] ([-IF input.rfk] [-OF output.html] | [filename.rfk])\n\n";
	print "options:\n\n";
	print " -f --full		Attemps to generate html for all rfk files below .\n";
	print " -i --interactive	Asks for confirmation before writing\n";
	print " -IF input.rfk		Full path of input rfk file (implies single)\n";
	print " -OF output.html	Full path of output html file (implies single)\n";
	print " -v --verbose		Display more information\n";
	print " -d --debug		Display more elaborate information (implies verbose)\n";
	print "\nSee http://tastytronic.net/asciiweb/ for more information.\n\n";

}
