#!/usr/bin/env bash


PARENT_DIRECTORY=/home/julien_joseph/Tortugas

################################# Filter the data #####################################

mkdir -p $PARENT_DIRECTORY/data/filtered

for file in $(ls $PARENT_DIRECTORY/data/raw); do

python3 $PARENT_DIRECTORY/scripts/filter_trajectory.py -odir $PARENT_DIRECTORY/data/filtered -i $PARENT_DIRECTORY/data/raw/$file -t 0.5

mv $PARENT_DIRECTORY/data/filtered/temp $PARENT_DIRECTORY/data/filtered/$file.filtered

done

############################### Plot individual trajectories ##########################

for file in $(ls $PARENT_DIRECTORY/data/filtered); do

python3 $PARENT_DIRECTORY/scripts/plot_individual_trajectory.py -i $PARENT_DIRECTORY/data/filtered/$file -o $PARENT_DIRECTORY/figures/$file.eps

done

############################### Split files by day of measure #########################

rm -r $PARENT_DIRECTORY/data/daily
mkdir $PARENT_DIRECTORY/data/daily

for file in $(ls $PARENT_DIRECTORY/data/filtered); do

sed 's/\//./g' $PARENT_DIRECTORY/data/filtered/$file > tmp

awk -v a="$PARENT_DIRECTORY/data/daily/$file." '{print>>a$3}' tmp

done

rm $PARENT_DIRECTORY/data/daily/*.date

############################### Plot daily positions ##################################

head -1 $PARENT_DIRECTORY/data/filtered/T010_2021.txt.filtered > header

for file in $(ls $PARENT_DIRECTORY/data/daily); do

cat header $PARENT_DIRECTORY/data/daily/$file > tmp
mv tmp $PARENT_DIRECTORY/data/daily/$file

done

rm header

python3 $PARENT_DIRECTORY/scripts/plot_all_trajectories.py -idir $PARENT_DIRECTORY/data/daily -o $PARENT_DIRECTORY/figures/daily_HR_sex.eps -c sex

python3 $PARENT_DIRECTORY/scripts/plot_all_trajectories.py -idir $PARENT_DIRECTORY/data/daily -o $PARENT_DIRECTORY/figures/daily_HR_season.eps -c season

############################### Plot distribution of daily home range ##################


python3 $PARENT_DIRECTORY/scripts/violins.py -idir $PARENT_DIRECTORY/data/daily -o $PARENT_DIRECTORY/figures/violin_sex.eps -c sex

python3 $PARENT_DIRECTORY/scripts/violins.py -idir $PARENT_DIRECTORY/data/daily -o $PARENT_DIRECTORY/figures/violin_season.eps -c season

############################### Plot distribution of turning angles ##################

python3 $PARENT_DIRECTORY/scripts/turning_angles.py -idir $PARENT_DIRECTORY/data/hilo_noviembre-diciembre_2020 -o $PARENT_DIRECTORY/figures/turning_angle.eps























