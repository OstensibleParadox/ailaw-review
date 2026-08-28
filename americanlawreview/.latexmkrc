use File::Path qw(make_path);

my $build_dir = 'build';
make_path($build_dir);

$out_dir = $build_dir;
$aux_dir = $build_dir;
$fdb_file = "$build_dir/$jobname.fdb_latexmk";
$emulate_aux_dir = 1;

my $texinputs = $ENV{TEXINPUTS} // '';
my $bibinputs = $ENV{BIBINPUTS} // '';
$ENV{TEXINPUTS} = ".:..:$texinputs";
$ENV{BIBINPUTS} = ".:examples:..:$bibinputs";

push @generated_exts, 'bcf', 'run.xml';
