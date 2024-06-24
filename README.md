### How to run

I reccommend using a virtual environment to install and run the program. If you don't wish to, skip to step 4

1. From the top level of the code (i.e. where this README is), create a virtual environment `python -m venv venv`
2. Activate the virtual environment `./venv/bin/activate` (assumes POSIX shell)
3. Install dependencies `pip install -r requirements.txt`
4. Run the submission file. The program takes the file location of a PDF to parse with the --path-to-case-pdf parameter. The output is quite verbose so I recommend piping it to an output file `python submission.py --path-to-case-pdf <file path> > ouput.txt`
5. The program will split the PDF into single pages, write them back to the same directory, then perform OCR on them, then submit for analysis.
6. If for whatever reason you cannot get it running, there is an example output in `example_output.txt`

### Things I would do differently/improvements:

1. The most obvious is change the way the PDFs are handled. Because the DocumentAI sync OCR service has a 15 page limit, in order to get around that I split the PDF into individual pages. This is not ideal for a couple of reasons, for example it's slower to split and upload individual pages, and some context may be missed if it exists over the end of one page and into another. The better solution would have been to upload the PDFs to an object store, and then use the batch document service which doesn't have this page limitation. Additionally, once stored, the PDF can be re-analysed or transformed at any time without having to re-upload. Splitting the PDFs into pages does make it easier to stay under context length limits though.
I chose not to use the batch service because I wasn't sure the test account this would be run on would have object store access.

2. The dates are a mess, as some are years, some are in dd/mm/yy format, some are in dd/mm/yyyy format, etc. With more time I would clean and normalise the dates, and probably store them as datetime values so they can be sorted better (i.e. properly).

3. Similarly, the generated events don't all make sense. A couple of them are probably too detailed for a quick analysis by a clinician. With more time we can refine the prompt and the output models to clean this up by adding it into different fields.

4. The generated DF ideally would be saved somewhere so we don't need to generate it again, probably into a database and also possibly a cache or feature store if we thought it may be requested soon. 

5. The whole "pipeline" is just code and data being passed around which doesn't scale well and is not fault tolerant. Ideally a production pipeline would look more like:
PDFs land in object store -> OCR and raw data is saved -> LLM -> structured data is saved. We'd use a job orchestrator to run the pipeline which would provide fault tolerance if a step fails, lineage for our data, and the ability to scale to demand.

6. With regard to model selection and prompting, I didn't experiment much. Gemini was obviously a lot better than other options after some simeple testing so I went with that. Given more time, LLM selection and prompt selection would be experimented on more to ensure we have a good choice.

7. Testing - all code should be unit tested, the GCP functions should be integration tested, and the LLM should be tested to ensure it's producing sensible outputs between code changes, ideally we could include an end to end test on sample data. 