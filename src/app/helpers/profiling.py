import cProfile, pstats, io

"""
profiling decorator
- place decorator before function to be profiled
- run test or program
- gather output in standard output
ex with post_mapping helper, place decorator befor method and run test using it from terminal:
python -m pytest -s tests\unit\mapping\test_mapping.py::test_post_mapping_with_content_as_string
"""
def profile(fnc):
    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()

        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        print(s.getvalue())
        return retval
    
    
    return inner

