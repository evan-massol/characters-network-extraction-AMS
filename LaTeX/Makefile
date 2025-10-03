 main: main.tex
	mkdir -p obj/
	xelatex -halt-on-error -output-directory obj/  main.tex
	BSTINPUTS=IEEEtran/bibtex/:$$BSTINPUTS bibtex obj/main
	xelatex -halt-on-error -output-directory obj/ main.tex
	xelatex -halt-on-error -output-directory obj/ main.tex

clean:
	rm -rf obj/



