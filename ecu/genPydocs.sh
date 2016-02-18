#!/bin/bash

basePath="${GitSrcDir}/exalogic_platform/automation/pqa/pylib/doc"

rm -rf ${basePath}/source/rst/*.rst
sphinx-apidoc -o ${basePath}/source/rst ${GitSrcDir}/exalogic_platform/automation/pqa/pylib
sphinx-apidoc -o ${basePath}/source/rst ${GitSrcDir}/oeca/install/pqa/tests/exalogic/ecu
cd ${basePath}
make html

pydirs[1]="exalogic_platform/automation/pqa"
pydirs[2]="oeca/install/pqa"

exit 0;

counter=0;
src_base_dir=$1

pydoc_dir=~/pydoc_dir

rm -rf $pydoc_dir
mkdir $pydoc_dir

echo ${#pydirs[@]}
while [ $counter -lt ${#pydirs[@]} ]; do
	counter=`expr $counter + 1`;
	cp -r $src_base_dir/${pydirs[$counter]} $pydoc_dir
done

export PYTHONPATH=$pydoc_dir/pqa

find $pydoc_dir -name "*.py" | xargs pydoc -w

pid=`pgrep pydoc`
echo "Old pydoc process id is:"$pid
echo "Killing old pydoc process"
kill -9 $pid
pid=`pgrep pydoc`
echo "Is old pydoc process still running:"$pid

cd $pydoc_dir
nohup pydoc -p 8081 &
pid=`pgrep pydoc`
echo "New pydoc process id:"$pid
