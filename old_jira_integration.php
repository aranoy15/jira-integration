<?php

namespace ApiBundle\Manager;

use ApiBundle\DomainService\FrontendUrlGenerator;
use ApiBundle\Dto\Zone\ZoneYoutrackIssueDto;
use ApiBundle\Entity\AdvertisementCategory;
use ApiBundle\Entity\Advertiser;
use ApiBundle\Entity\Campaign;
use ApiBundle\Entity\ExternalOffer;
use ApiBundle\Entity\GeoGroup;
use ApiBundle\Entity\Product;
use ApiBundle\Entity\ProductLimit;
use ApiBundle\Entity\ProductRate;
use ApiBundle\Entity\Rate;
use ApiBundle\Entity\RateRevenue;
use ApiBundle\Entity\TrafficType;
use ApiBundle\Entity\User;
use ApiBundle\Entity\WorkModel;
use ApiBundle\Enum\Advertiser\AdvertiserDepartmentTypeEnum;
use ApiBundle\Enum\AdvertiserTypeEnum;
use ApiBundle\Enum\Campaign\RevenueTypeEnum;
use ApiBundle\Enum\LimitEnum;
use ApiBundle\Enum\YouTrack\YouTrackUserEnum;
use ApiBundle\Manager\YouTrack\IssueManagerInterface;
use ApiBundle\Service\Model\Issue;
use ApiBundle\Service\YoutrackApi;
use Doctrine\ORM\EntityManagerInterface;
use JMS\Serializer\Serializer;
use JMS\Serializer\SerializerInterface;

final class YoutrackManager
{
    /**
     * @var EntityManagerInterface
     */
    private $entityManager;

    /**
     * @var YoutrackApi
     */
    private $api;

    /**
     * @var IssueManagerInterface
     */
    private $issueManager;

    /**
     * @var Serializer
     */
    private $serializer;

    /**
     * @var FrontendUrlGenerator
     */
    private FrontendUrlGenerator $frontendUrlGenerator;

    /**
     * @param EntityManagerInterface $entityManager
     * @param YoutrackApi            $api
     * @param IssueManagerInterface  $issueManager
     * @param SerializerInterface    $serializer
     * @param FrontendUrlGenerator   $frontendUrlGenerator
     */
    public function __construct(
        EntityManagerInterface $entityManager,
        YoutrackApi $api,
        IssueManagerInterface $issueManager,
        SerializerInterface $serializer,
        FrontendUrlGenerator $frontendUrlGenerator
    ) {
        $this->entityManager = $entityManager;
        $this->api = $api;
        $this->issueManager = $issueManager;
        $this->serializer = $serializer;
        $this->frontendUrlGenerator = $frontendUrlGenerator;
    }

    /**
     * @param string $url
     * @param string $name
     *
     * @return string
     */
    public static function getLink(string $url, string $name): string
    {
        return "{html}<a href=\"$url\">$name</a>{html}";
    }

    /**
     * @param string $url
     * @param string $name
     *
     * @return string
     */
    public static function getMDLink(string $url, string $name): string
    {
        return '[' . $name . '](' . $url . ')';
    }

    /**
     * @param string $string
     *
     * @return string
     */
    public static function wrapInHtml(string $string): string
    {
        return '{html}' . $string . '{html}';
    }

    /**
     * @param string $string
     * @param string $language
     *
     * @return string
     */
    public static function wrapInCode(string $string, string $language = 'json'): string
    {
        return "{code lang=$language}$string{code}";
    }

    /**
     * @param array $array
     *
     * @return string
     */
    public function arrayToFormattedString(array $array): string
    {
        $result = '';
        foreach ($array as $key => $value) {
            if (\is_array($value)) {
                if (!\is_numeric($key)) {
                    $result .= '<strong>' . $key . '</strong>: ' . $this->arrayToFormattedString($value);
                } else {
                    $result .= $this->arrayToFormattedString($value);
                }
            } else {
                if (!\is_numeric($key)) {
                    $result .= '<strong>' . $key . '</strong>: ' . $value . '<br>';
                } else {
                    $result .= '<li>' . $value . '</li>';
                }
            }
        }

        return $result;
    }

    /**
     * Converts different values for good view in YT.
     *
     * @param mixed $value
     *
     * @return string
     */
    public function allFormatsToString($value): string
    {
        switch (\gettype($value)) {
            case 'array':
                $newValue = $this->arrayToFormattedString($value);

                break;
            case 'object':
                $value = $this->serializer->toArray($value);
                $newValue = $this->arrayToFormattedString($value);

                break;
            case 'boolean':
                $newValue = $value ? 'true' : 'false';

                break;
            default:
                $newValue = (string) $value;
        }

        return self::wrapInHtml($newValue);
    }

    /**
     * @param ExternalOffer $externalOffer
     * @param Product       $product
     * @param array         $changes
     */
    public function addCommentForLimits(ExternalOffer $externalOffer, Product $product, array $changes): void
    {
        if (null !== $externalOffer->getIssue()) {
            $issueId = $externalOffer->getIssue();
            $body = $this->api->getTableHeader([
                ' Product limit ',
                ' old values ',
                ' new values ',
            ]);
            foreach ($changes as $key => $value) {
                $value[0][0]['period'] = \ucfirst(ProductLimit::$periods[$value[0][0]['period']]);
                $value[1][0]['period'] = \ucfirst(ProductLimit::$periods[$value[1][0]['period']]);
                $value[0][0]['type'] = \ucfirst(LimitEnum::DEPRECATED_TYPE_LIST[$value[0][0]['type']]);
                $value[1][0]['type'] = \ucfirst(LimitEnum::DEPRECATED_TYPE_LIST[$value[1][0]['type']]);

                $link = $this->frontendUrlGenerator->getLinkToEntity($product);
                $body .= $this->api->getTableLine([
                    self::getLink($link, $product->getName()),
                    $this->allFormatsToString($value[0]),
                    $this->allFormatsToString($value[1]),
                ]);
            }
            $this->api->addCommentToIssue($issueId, $body);
        }
    }

    public function addCommentForStartedCampaigns(array $products): void
    {
        foreach ($products as $row) {
            if (empty($row[0]['last_stopped_at'])) {
                $timeDiff = '0';
            } else {
                $timeDiff = $this->timestampRangeToCompactFormat($row[0]['last_stopped_at']->getTimestamp(), \time());
            }
            $issueId = $row[0]['issue_id'];
            $body = 'Relaunched campaigns after domain block: (stop time: ' . $timeDiff . ')' . PHP_EOL;
            foreach ($row as $campaign) {
                $link = $this->frontendUrlGenerator->getLinkToClassName(Campaign::class, $campaign['campaign_id']);
                $body .= "[{$campaign['campaign_id']}]($link) - {$campaign['campaign_name']}" . PHP_EOL;
            }
            $this->api->addCommentToIssue($issueId, $body);
        }
    }

    public function addCommentForStoppedCampaigns(array $products): void
    {
        foreach ($products as $row) {
            $issueId = $row[0]['issue_id'];
            $body = 'Campaigns stopped by domain block:' . PHP_EOL;
            foreach ($row as $campaign) {
                $link = $this->frontendUrlGenerator->getLinkToClassName(Campaign::class, $campaign['campaign_id']);
                $body .= "[{$campaign['campaign_id']}]($link) - {$campaign['campaign_name']}" . PHP_EOL;
            }
            $this->api->addCommentToIssue($issueId, $body);
        }
    }

    /**
     * @param Product    $product
     * @param User       $creator
     * @param Campaign[] $campaigns
     *
     * @throws \Exception
     *
     * @return Issue
     */
    public function createIssueFromProduct(Product $product, User $creator, $campaigns = []): Issue
    {
        $advertiser = $product->getAdvertiser();
        $currentDate = new \DateTime();
        $repo = $this->entityManager->getRepository(RateRevenue::class);

        $rateToString = \Closure::fromCallable([$this, 'rateToString']);
        $campaignToString = \Closure::fromCallable([$this, 'campaignToString']);

        if (\count($campaigns) < 0) {
            $campaigns = $product->getCampaigns()->toArray();
        }

        $campaignIds = \array_map(static fn (Campaign $campaign) => $campaign->getId(), $campaigns);

        $campaigns = \array_map(
            function (Campaign $campaign) use ($currentDate, $repo, $campaignToString, $rateToString) {
                $rates = $repo->findOpenRatesByDate(
                    $campaign,
                    $currentDate
                );
                $rates = \array_map($rateToString, $rates);

                return
                    $campaignToString($campaign)
                    . (
                        \count($rates) > 0
                        ? PHP_EOL . \implode(PHP_EOL, $rates)
                        : ''
                    )
                    . PHP_EOL
                ;
            },
            $campaigns
        )
        ;

        $advertiserLink = $this->frontendUrlGenerator->getLinkToEntity($advertiser);
        $productLink = $this->frontendUrlGenerator->getLinkToEntity($product);
        $categoryNames = \implode(', ', $product->getCategories()->map(
            static fn (AdvertisementCategory $category) => $category->getName()
        )->toArray());
        $settings = $this->getProductSettingsString($product);
        $rates = '';
        if (RevenueTypeEnum::PARSED !== $product->getRevenueType()) {
            $rates = \array_map($rateToString, $product->getRates()->toArray());
            $rates = '* Rates: ' . PHP_EOL . \implode(PHP_EOL, $rates) . PHP_EOL;
        }

        $limits = \array_map([$this, 'limitToString'], $product->getLimits()->toArray());
        $limits = \count($limits) > 0
            ? '* Limits: ' . PHP_EOL . \implode(PHP_EOL, $limits) . PHP_EOL
            : '';
        $data = [
            $creator->getName(),
            $advertiserLink,
            $productLink,
            $product->getPreviewUrl(),
            $product->getKpi(),
            $categoryNames,
            RevenueTypeEnum::LABELS[$product->getRevenueType()],
            $settings,
            $rates,
            $limits,
            \implode(PHP_EOL, $campaigns),
            \implode(',', $campaignIds),
        ];
        $description = \str_replace(
            Issue::PRODUCT_TO_REPLACE,
            $data,
            Issue::getProductTemplateMD()
        );
        $issue = $this->issueManager
            ->createIssue(Issue::PROJECT_OPTIMIZATION)
            ->setTypeTask(Issue::TASK_ADV)
            ->setSummary(
                $advertiser->getId() . ' | ' . $advertiser->getName() . ' - '
                . $product->getName() . ' (' . $product->getId() . ')'
            )
            ->setDescription($description)
            ->addWatcher(YouTrackUserEnum::D_PACHKO)
            ->setCreator($creator)
            ->setPriority($advertiser->isNew() ? 'Major' : 'Normal')
        ;
        if (null !== ($watcher = $creator->getYoutrackLogin())) {
            $issue->addWatcher($watcher);
        }

        return $issue;
    }

    public function createIssueFromAdvertiser(Advertiser $advertiser, User $creator): Issue
    {
        $advertiserLink = $this->frontendUrlGenerator->getLinkToEntity($advertiser);
        $geos = $advertiser->getGeoGroups()->map(static fn (GeoGroup $gg) => $gg->getName())->toArray();
        $workModels = $advertiser->getWorkModels()->map(static fn (WorkModel $wm) => $wm->getName())->toArray();
        $trafficTypes = $advertiser->getTrafficTypes()->map(static fn (TrafficType $tt) => $tt->getName())->toArray();
        $revenueType = $advertiser->getRevenueType();
        $monthlySpend = $advertiser->getMonthlySpend();
        $managerComment = $advertiser->getManagerComment();

        $separator = ', ';
        $data = [];
        $template = '';
        $searchQuery = '';

        if (AdvertiserDepartmentTypeEnum::SSP === $advertiser->getDepartment()) {
            $template = Issue::getSspAdvertiserTemplate();
            $searchQuery = Issue::SSP_ADVERTISER_TO_REPLACE;

            $data = [
                $creator->getName(),
                $advertiserLink,
                RevenueTypeEnum::LABELS[$revenueType] ?? null,
                $monthlySpend,
                $managerComment,
            ];
        }

        if (AdvertiserDepartmentTypeEnum::SSP !== $advertiser->getDepartment()) {
            $template = Issue::getAdvertiserTemplate();
            $searchQuery = Issue::ADVERTISER_TO_REPLACE;

            $data = [
                $creator->getName(),
                $advertiserLink,
                \implode($separator, $geos),
                \implode($separator, $workModels),
                \implode($separator, $trafficTypes),
                $advertiser->getLandingInfo(),
                AdvertiserTypeEnum::LABELS[$advertiser->getType()],
            ];
        }

        $description = \str_replace(
            $searchQuery,
            $data,
            $template
        );

        $issue = $this->issueManager
            ->createIssue(Issue::PROJECT_OPTIMIZATION)
            ->setTypeTask(Issue::TASK_ADV)
            ->setSummary($advertiser->getId() . ' | ' . $advertiser->getName())
            ->setDescription($description)
            ->setAssignee(AdvertiserDepartmentTypeEnum::SSP === $advertiser->getDepartment() ? YouTrackUserEnum::V_KALMYKOV : YouTrackUserEnum::E_MALIHINA)
            ->setCreator($creator)
        ;
        if (null !== ($watcher = $creator->getYoutrackLogin())) {
            $issue->addWatcher($watcher);
        }

        return $issue;
    }

    public function createIssueFromZone(ZoneYoutrackIssueDto $dto, User $creator): Issue
    {
        return $this->issueManager
            ->createIssue(Issue::PROJECT_OPTIMIZATION)
            ->setTypeTask(Issue::TASK_PUB)
            ->setSummary($dto->summary)
            ->setDescription($dto->description)
            ->setCreator($creator)
        ;
    }

    /**
     * @param string $issueId
     * @param Issue  $issue
     */
    public function updateIssueParams(string $issueId, Issue $issue): void
    {
        $this->api->updateIssueParams($issueId, $issue);
    }

    /**
     * @param Issue $issue
     *
     * @return string
     */
    public function sendIssueToYouTrack(Issue $issue): string
    {
        return $this->api->createIssue($issue);
    }

    /**
     * @param Rate $rate
     *
     * @return string
     */
    public function rateToString(Rate $rate): string
    {
        $value = '';
        if ($rate instanceof RateRevenue || $rate instanceof ProductRate) {
            $value = $rate->getPrice();
        }

        return '  * '
            . $rate->getType() . ': '
            . \implode(', ', $rate->getGeo()) . ' - '
            . $value . ' ' . $rate->getCurrency()
            . PHP_EOL
        ;
    }

    /**
     * @param ProductLimit $limit
     *
     * @return string
     */
    public function limitToString(ProductLimit $limit): string
    {
        return '  * '
            . $limit->getTypeTitle() . ': '
            . $limit->getPeriodName() . ' - '
            . $limit->getValue()
            . PHP_EOL
        ;
    }

    public function campaignToString(Campaign $campaign): string
    {
        return '* ' . self::getMDLink(
            $this->frontendUrlGenerator->getLinkToEntity($campaign),
            $campaign->getId() . ' ' . $campaign->getName()
        );
    }

    private function getProductSettingsString(Product $product): string
    {
        $settings = '* Settings: ' . PHP_EOL;
        $settings .= '  - With preland: ' . ($product->isWithPreland() ? 'Yes' : 'No') . PHP_EOL;
        $settings .= '  - Direct link: ' . ($product->isDirectLink() ? 'Yes' : 'No') . PHP_EOL;
        $settings .= '  - Without direct link: ' . ($product->isWithoutDirectLink() ? 'Yes' : 'No') . PHP_EOL;

        return $settings;
    }

    private function timestampRangeToCompactFormat(int $timestampStart, int $timestampEnd): string
    {
        $diff = $timestampEnd - $timestampStart;
        $days = \floor($diff / (24 * 60 * 60));
        $diff -= $days * 24 * 60 * 60;
        $hours = \floor($diff / (60 * 60));
        $diff -= $hours * 60 * 60;
        $minutes = \floor($diff / 60);
        $diff -= $minutes * 60;
        $seconds = $diff;
        $timeStr = '';
        if ($days > 0) {
            $timeStr .= $days . 'd ';
        }
        if ($hours > 0) {
            $timeStr .= $hours . 'h ';
        }
        if ($minutes > 0) {
            $timeStr .= $minutes . 'm ';
        }
        if ($seconds > 0) {
            $timeStr .= $seconds . 's';
        }

        return $timeStr;
    }
}
