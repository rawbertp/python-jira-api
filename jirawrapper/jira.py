import atlassian
import concurrent.futures
import time
import logging

logger = logging.getLogger(__name__)


class Jira(atlassian.Jira):
    """
    Wrapper for the official https://github.com/atlassian-api/atlassian-python-api with multi-threaded search
    """

    def __init__(self, url, token=None, username=None, password=None, workers=5, **kwargs):
        self.workers = workers
        super().__init__(url=url, token=token, username=username, password=password, **kwargs)

    def __get_count(self, jql):
        res = self.jql(jql, limit=0)
        if 'total' not in res or res['total'] == 0:
            logger.warning('No issues found for JQL: [%s]' % jql)
            return 0

        total = res['total']
        logger.info('%s issues found...' % total)

        return total

    def issue_get_worklog(self, issue_key):
        return super().issue_get_worklog(issue_id_or_key=issue_key)['worklogs']

    def search(self, jql, fields='*all', expand='', bucket_size=50):
        """
        Perform a multi-threaded search based on `workers` setting.
        :param jql: JQL query to execute
        :param fields: Fields to return
        :param expand: Fields to expand
        :param bucket_size: Size of the individual buckets
        :return: Search results (dict)
        """
        logger.debug('Query: %s' % jql)

        start = time.time()
        issues = []

        # get the number of issues
        total = self.__get_count(jql)

        def execute_jql(jql, max_results, start_at, expand, fields):
            def execute():
                return self.jql(jql, expand=expand, limit=max_results, start=start_at, fields=fields)

            return execute

        i = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = []
            while True:
                task = execute_jql(jql=jql, max_results=bucket_size, start_at=i, expand=expand, fields=fields)
                futures.append(executor.submit(task))

                if i >= total:
                    break

                i += bucket_size

            for future in concurrent.futures.as_completed(futures):
                issues += future.result()['issues']

        logger.info("Fetched %s issues in %s seconds" % (len(issues), round((time.time() - start), 2)))

        if len(issues) != total:
            logger.error('Number of fetched issues (%s) does NOT match reported total (%s)!' % (len(issues), total))

        return issues
