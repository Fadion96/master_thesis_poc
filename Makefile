.PHONY: clean

all: clean dvs mdvs

dvs:
		g++ dvs.cpp -o dvs -std=c++17 -lgmpxx -lgmp /usr/local/lib/libmcl.a 
mdvs:
		g++ mdvs.cpp -o mdvs -std=c++17 -lgmpxx -lgmp /usr/local/lib/libmcl.a 
clean:
		rm -f *.o dvs mdvs
