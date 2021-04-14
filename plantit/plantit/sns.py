import json
import logging
import boto3
from botocore.exceptions import ClientError
import os

logger = logging.getLogger(__name__)


# from https://docs.aws.amazon.com/code-samples/latest/catalog/python-sns-sns_basics.py.html
class SnsWrapper:
    """Encapsulates Amazon SNS topic and subscription functions."""
    def __init__(self, sns_resource):
        """
        :param sns_resource: A Boto3 Amazon SNS resource.
        """
        self.sns_resource = sns_resource

    def create_topic(self, name):
        """
        Creates a notification topic.

        :param name: The name of the topic to create.
        :return: The newly created topic.
        """
        try:
            topic = self.sns_resource.create_topic(Name=name)
            logger.info(f"Created topic {name} with ARN {topic['TopicArn']}")
        except ClientError:
            logger.exception(f"Couldn't create topic {name}.")
            raise
        else:
            return topic

    def list_topics(self):
        """
        Lists topics for the current account.

        :return: An iterator that yields the topics.
        """
        try:
            topics_iter = self.sns_resource.topics.all()
            logger.info("Got topics.")
        except ClientError:
            logger.exception("Couldn't get topics.")
            raise
        else:
            return topics_iter

    def delete_topic(self, arn):
        """
        Deletes a topic. All subscriptions to the topic are also deleted.
        """
        try:
            self.sns_resource.delete_topic(TopicArn=arn)
            logger.info("Deleted topic %s.", arn)
        except ClientError:
            logger.exception("Couldn't delete topic %s.", arn)
            raise

    def subscribe(self, arn, protocol, endpoint):
        """
        Subscribes an endpoint to the topic. Some endpoint types, such as email,
        must be confirmed before their subscriptions are active. When a subscription
        is not confirmed, its Amazon Resource Number (ARN) is set to
        'PendingConfirmation'.

        :param topic: The topic to subscribe to.
        :param protocol: The protocol of the endpoint, such as 'sms' or 'email'.
        :param endpoint: The endpoint that receives messages, such as a phone number
                         (in E.164 format) for SMS messages, or an email address for
                         email messages.
        :return: The newly added subscription.
        """
        try:
            subscription = self.sns_resource.subscribe(
                TopicArn=arn,
                Protocol=protocol,
                Endpoint=endpoint,
                ReturnSubscriptionArn=True)
            logger.info("Subscribed %s %s to topic %s.", protocol, endpoint, arn)
        except ClientError:
            logger.exception(
                "Couldn't subscribe %s %s to topic %s.", protocol, endpoint, arn)
            raise
        else:
            return subscription

    def list_subscriptions(self, topic_arn=None):
        """
        Lists subscriptions for the current account, optionally limited to a
        specific topic.

        :param topic_arn: When specified, only subscriptions to this topic are returned.
        :return: An iterator that yields the subscriptions.
        """
        try:
            if topic_arn is None:
                subs_iter = self.sns_resource.subscriptions.all()
            else:
                subs_iter = self.sns_resource.list_subscriptions_by_topic(TopicArn=topic_arn)
            logger.info("Got subscriptions.")
        except ClientError:
            logger.exception("Couldn't get subscriptions.")
            raise
        else:
            return subs_iter

    @staticmethod
    def add_subscription_filter(subscription, attributes):
        """
        Adds a filter policy to a subscription. A filter policy is a key and a
        list of values that are allowed. When a message is published, it must have an
        attribute that passes the filter or it will not be sent to the subscription.

        :param subscription: The subscription the filter policy is attached to.
        :param attributes: A dictionary of key-value pairs that define the filter.
        """
        try:
            att_policy = {key: [value] for key, value in attributes.items()}
            subscription.set_attributes(
                AttributeName='FilterPolicy', AttributeValue=json.dumps(att_policy))
            logger.info("Added filter to subscription %s.", subscription.arn)
        except ClientError:
            logger.exception(
                "Couldn't add filter to subscription %s.", subscription.arn)
            raise

    def delete_subscription(self, arn):
        """
        Unsubscribes and deletes a subscription.
        """
        try:
            self.sns_resource.unsubscribe(SubscriptionArn=arn)
            logger.info("Deleted subscription %s.", arn)
        except ClientError:
            logger.exception("Couldn't delete subscription %s.", arn)
            raise

    def publish_text_message(self, phone_number, message):
        """
        Publishes a text message directly to a phone number without need for a
        subscription.

        :param phone_number: The phone number that receives the message. This must be
                             in E.164 format. For example, a United States phone
                             number might be +12065550101.
        :param message: The message to send.
        :return: The ID of the message.
        """
        try:
            response = self.sns_resource.meta.client.publish(
                PhoneNumber=phone_number, Message=message)
            message_id = response['MessageId']
            logger.info("Published message to %s.", phone_number)
        except ClientError:
            logger.exception("Couldn't publish message to %s.", phone_number)
            raise
        else:
            return message_id

    def publish_message(self, topic_arn, subject, message, attributes):
        """
        Publishes a message, with attributes, to a topic. Subscriptions can be filtered
        based on message attributes so that a subscription receives messages only
        when specified attributes are present.

        :param topic_arn: The topic to publish to.
        :param message: The message to publish.
        :param attributes: The key-value attributes to attach to the message. Values
                           must be either `str` or `bytes`.
        :return: The ID of the message.
        """
        try:
            att_dict = {}
            for key, value in attributes.items():
                if isinstance(value, str):
                    att_dict[key] = {'DataType': 'String', 'StringValue': value}
                elif isinstance(value, bytes):
                    att_dict[key] = {'DataType': 'Binary', 'BinaryValue': value}
            response = self.sns_resource.publish(TopicArn=topic_arn, Subject=subject, Message=message, MessageAttributes=att_dict)
            message_id = response['MessageId']
            logger.info("Published message with attributes %s to topic %s.", attributes, topic_arn)
        except ClientError:
            logger.exception("Couldn't publish message to topic %s.", topic_arn)
            raise
        else:
            return message_id

    def publish_multi_message(
            self, arn, subject, default_message, sms_message, email_message):
        """
        Publishes a multi-format message to a topic. A multi-format message takes
        different forms based on the protocol of the subscriber. For example,
        an SMS subscriber might receive a short, text-only version of the message
        while an email subscriber could receive an HTML version of the message.

        :param topic: The topic to publish to.
        :param subject: The subject of the message.
        :param default_message: The default version of the message. This version is
                                sent to subscribers that have protocols that are not
                                otherwise specified in the structured message.
        :param sms_message: The version of the message sent to SMS subscribers.
        :param email_message: The version of the message sent to email subscribers.
        :return: The ID of the message.
        """
        try:
            message = {
                'default': default_message,
                'sms': sms_message,
                'email': email_message
            }
            response = self.sns_resource.publish(
                TopicArn=arn,
                Message=json.dumps(message), Subject=subject, MessageStructure='json')
            message_id = response['MessageId']
            logger.info("Published multi-format message to topic %s.", arn)
        except ClientError:
            logger.exception("Couldn't publish message to topic %s.", arn)
            raise
        else:
            return message_id


class SnsClient:
    __client = None

    @staticmethod
    def get():
        if SnsClient.__client is None:
            boto3.setup_default_session(region_name=os.environ.get('AWS_REGION'))
            SnsClient.__client = SnsWrapper(boto3.client(
                'sns',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')))
        return SnsClient.__client


def get_sns_subscription_status(topic_arn):
    sns = SnsClient.get()
    subs = sns.list_subscriptions(topic_arn)['Subscriptions']
    if len(subs) == 1:
        sub = subs[0]
        if sub['SubscriptionArn'] == 'PendingConfirmation':
            return 'pending'
        else:
            return 'enabled'
    else:
        return 'disabled'
